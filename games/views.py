from django.http import Http404
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, FormView
from django.conf import settings

from braces.views import LoginRequiredMixin

from .models import Game, Release, CrashReport
from .forms import LoveForm

from games import tasks


def get_game(request, uuid):
    game = get_object_or_404(Game, uuid=uuid)

    if game.owner != request.user:
        raise Http404

    return game


class UUIDMixin(object):
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'


class GameDetail(UUIDMixin, LoginRequiredMixin, DetailView):
    model = Game
    context_object_name = 'game'

    def get_context_data(self, **kwargs):
        context = super(GameDetail, self).get_context_data(**kwargs)

        if context['game'].owner != self.request.user:
            raise Http404

        context['KEEN_PROJECT_ID'] = settings.KEEN_PROJECT_ID
        context['KEEN_READ_KEY'] = settings.KEEN_READ_KEY

        return context


class ReportList(LoginRequiredMixin, ListView):
    model = CrashReport

    def get_queryset(self):
        self.game = get_game(self.request, self.kwargs['uuid'])
        return CrashReport.objects.filter(game=self.game).order_by('-created')

    def get_context_data(self, **kwargs):
        context = super(ReportList, self).get_context_data(**kwargs)
        context['game'] = self.game
        return context


class ReleaseList(LoginRequiredMixin, ListView):
    model = Release

    def get_queryset(self):
        self.game = get_game(self.request, self.kwargs['uuid'])
        return Release.objects.filter(game=self.game).order_by('-created')

    def get_context_data(self, **kwargs):
        context = super(ReleaseList, self).get_context_data(**kwargs)
        context['game'] = self.game
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

        # Get the latest release for the game, and increment the version
        version = game.next_version()
        release = game.release_set.create(version=version)

        # FIXME: Abstract this away
        f = form.cleaned_data['lovefile']
        f.name = "{}-original-{}.love".format(game.slug, version)

        release.add_asset(f, tag='uploaded')

        tasks.lovepackage.delay(release.pk)

        return super(ReleaseCreate, self).form_valid(form)


class GameCreate(LoginRequiredMixin, CreateView):
    model = Game
    fields = ['name', 'framework']

    def form_valid(self, form):
        form.instance.owner = self.request.user
        form.instance.slug = slugify(form.instance.name)
        return super(GameCreate, self).form_valid(form)
