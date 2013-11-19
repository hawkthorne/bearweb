from django.views.generic.edit import CreateView
from .models import Game
from braces.views import LoginRequiredMixin


class GameCreate(LoginRequiredMixin, CreateView):
    model = Game
    fields = ['name']

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(AuthorCreate, self).form_valid(form)
