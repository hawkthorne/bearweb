from django.conf import settings
from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from games.views import download, IdenticonDetail
from core.views import ContactView, PricingView
from blog.views import ArticleView


def template(path):
    return TemplateView.as_view(template_name=path)

urlpatterns = patterns(
    '',
    url((r'^games/(?P<uuid>[0-9a-f]{24})/download/'
         r'(?P<platform>windows|osx|love)$'),
        download, name='download'),
    url(r'^identicons/(?P<uuid>[0-9a-f]{24}).png', IdenticonDetail.as_view(),
        name='identicon'),
    url(r'api/', include('games.urls.legacy', namespace='api')),
    url(r'^$', template("core/index.html"), name='home'),
    url(r'^robots.txt$', TemplateView.as_view(template_name='core/robots.txt',
                                              content_type='text/plain')),
    url(r'^pricing$', PricingView.as_view(), name='pricing'),
    url(r'^privacy$', template('core/privacy.html'), name='privacy'),
    url(r'^tos$', template('core/tos.html'), name='tos'),
    url(r'^contact$', ContactView.as_view(), name='contact'),

    url(r'^blog$', template('blog/index.html'), name='blog'),
    url(r'^blog/feed.xml$', template('blog/feed.xml'), name='feed'),
    url(r'^blog/(?P<article_name>[a-z0-9\-]+)$', ArticleView.as_view()),

    url(r'^houston/', include(admin.site.urls)),

)

if settings.DEBUG:
    urlpatterns += patterns(
        '',
        (r'^500/$', 'django.views.defaults.server_error'),
        (r'^404/$', 'django.views.defaults.page_not_found'),
    )
