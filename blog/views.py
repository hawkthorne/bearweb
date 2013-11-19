import os

from django.views.generic import TemplateView


class ArticleView(TemplateView):

    def get_template_names(self):
        article_name = self.kwargs.get('article_name', 'notfound')
        return [os.path.join('blog', 'blog', article_name, 'index.html')]
