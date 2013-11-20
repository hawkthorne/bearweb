from django.http import Http404
from django.template.defaultfilters import slugify
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView

from braces.views import LoginRequiredMixin

from .models import Game, Release


class GameDetail(LoginRequiredMixin, DetailView):
    model = Game
    context_object_name = 'game'

    def get_context_data(self, **kwargs):
        context = super(GameDetail, self).get_context_data(**kwargs)

        if context['game'].owner != self.request.user:
            raise Http404

        return context


class ReleaseList(LoginRequiredMixin, ListView):
    model = Release

    def get_queryset(self):
        self.game = get_object_or_404(Game, pk=self.kwargs['pk'])

        if self.game.owner != self.request.user:
            raise Http404

        return Release.objects.filter(game=self.game)

    def get_context_data(self, **kwargs):
        context = super(ReleaseList, self).get_context_data(**kwargs)
        context['game'] = self.game
        return context


class GameCreate(LoginRequiredMixin, CreateView):
    model = Game
    fields = ['name', 'framework']

    def form_valid(self, form):
        form.instance.owner = self.request.user
        form.instance.slug = slugify(form.instance.name)
        return super(GameCreate, self).form_valid(form)
