import os

from django.views.generic import TemplateView
from django.template.base import TemplateDoesNotExist
from django.http import Http404
from django.template.loader import get_template


class ArticleView(TemplateView):

    def get_template_names(self):
        article_name = self.kwargs.get('article_name', 'notfound')
        template = os.path.join('blog', 'blog', article_name, 'index.html')

        try:
            get_template(template)
        except TemplateDoesNotExist:
            raise Http404

        return [template]
