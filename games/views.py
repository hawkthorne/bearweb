from django.http import Http404
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.core.urlresolvers import reverse
from django.utils.cache import patch_response_headers
from django.template.defaultfilters import slugify
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.views.decorators.http import require_safe
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, FormView, UpdateView
from django.conf import settings

from braces.views import LoginRequiredMixin

from .models import Game, Release, CrashReport
from .forms import LoveForm, GameForm, UpdateGameForm

from games import bundle
from games import tasks


def get_game(request, uuid):
    game = get_object_or_404(Game, uuid=uuid)

    if game.owner != request.user:
        raise Http404

    return game


class UUIDMixin(object):
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'


class IdenticonDetail(UUIDMixin, DetailView):
    model = Game
    context_object_name = 'game'

    def render_to_response(self, context, **kwargs):
        response = HttpResponse(content_type="image/png")

        image = context['game'].identicon(56)
        image.save(response, 'PNG')

        patch_response_headers(response, cache_timeout=31536000)

        return response


class GameDetail(UUIDMixin, LoginRequiredMixin, DetailView):
    model = Game
    context_object_name = 'game'

    def get_context_data(self, **kwargs):
        context = super(GameDetail, self).get_context_data(**kwargs)

        if context['game'].owner != self.request.user:
            raise Http404

        game = context['game']

        context['KEEN_PROJECT_ID'] = settings.KEEN_PROJECT_ID
        context['KEEN_READ_KEY'] = settings.KEEN_READ_KEY
        context['releases'] = game.release_set.order_by('-created')[:10]
        context['crash_reports'] = \
            game.crashreport_set.order_by('-created')[:5]
        return context


class ReportList(LoginRequiredMixin, ListView):
    model = CrashReport
    context_object_name = 'crash_reports'

    def get_queryset(self):
        self.game = get_game(self.request, self.kwargs['uuid'])
        return self.game.crashreport_set.order_by('-created')

    def get_context_data(self, **kwargs):
        context = super(ReportList, self).get_context_data(**kwargs)
        context['game'] = self.game
        return context


class ReleaseList(LoginRequiredMixin, ListView):
    model = Release
    context_object_name = 'releases'

    def get_queryset(self):
        self.game = get_game(self.request, self.kwargs['uuid'])
        return Release.objects.filter(game=self.game).order_by('-created')

    def get_context_data(self, **kwargs):
        context = super(ReleaseList, self).get_context_data(**kwargs)
        context['game'] = self.game
        context['show_love_version'] = True
        return context


class ReleaseCreate(LoginRequiredMixin, FormView):
    template_name = 'games/release_form.html'
    form_class = LoveForm

    def get_success_url(self):
        return reverse('games:releases', kwargs={'uuid': self.kwargs['uuid']})

    def get_context_data(self, **kwargs):
        context = super(ReleaseCreate, self).get_context_data(**kwargs)
        context['game'] = get_game(self.request, self.kwargs['uuid'])
        return context

    def form_valid(self, form):
        game = get_game(self.request, self.kwargs['uuid'])

        f = form.cleaned_data['lovefile']
        version = form.cleaned_data['version']

        if not game.valid_version(version):
            errors = {
                'invalid_version': version,
                'game': game,
            }
            partial = render_to_string('games/upload_errors.html', errors)
            return HttpResponseBadRequest(partial)

        if not bundle.check_for_main(f):
            errors = {'invalid_file': True}
            partial = render_to_string('games/upload_errors.html', errors)
            return HttpResponseBadRequest(partial)

        love_version = bundle.detect_version(f) or "0.8.0"

        # Get the latest release for the game, and increment the version
        release = game.release_set.create(version=version,
                                          love_version=love_version)

        # FIXME: Abstract this away
        f.name = "{}-original-{}.love".format(game.slug, version)

        release.add_asset(f, tag='uploaded')

        tasks.lovepackage.delay(release.pk)

        return super(ReleaseCreate, self).form_valid(form)


class GameCreate(LoginRequiredMixin, CreateView):
    model = Game
    form_class = GameForm

    def form_valid(self, form):
        form.instance.owner = self.request.user
        form.instance.slug = slugify(form.instance.name)
        return super(GameCreate, self).form_valid(form)


class GameUpdate(LoginRequiredMixin, UpdateView):
    model = Game
    template_name_suffix = '_update_form'
    context_object_name = 'game'
    form_class = UpdateGameForm

    def get_object(self, queryset=None):
        return get_game(self.request, self.kwargs['uuid'])

    def form_valid(self, form):
        form.instance.slug = slugify(form.instance.name)
        return super(GameUpdate, self).form_valid(form)


@require_safe
def download(request, uuid, platform):

    game = get_object_or_404(Game, uuid=uuid)

    if not game.public:
        raise Http404

    if platform not in ['windows', 'osx']:
        raise Http404

    try:
        release = game.latest_release()
    except IndexError:
        raise Http404

    if platform == "windows":
        url = release.windows_url()
    else:
        url = release.osx_url()

    if not url:
        raise Http404

    return redirect(url)
