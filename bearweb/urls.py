from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from core.views import ContactView, PortalView, PricingView
from core.views import Dashboard, user_redirect
from blog.views import ArticleView


def template(path):
    return TemplateView.as_view(template_name=path)


urlpatterns = patterns(
    '',
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout',
        {'next_page': '/'}),
    url(r'^games/', include('games.urls', namespace='games')),
    url(r'^api/', include('games.api_urls', namespace='api')),
    url(r'^accounts/', include('registration.backends.simple.urls')),
    url(r'^$', template("core/index.html"), name='home'),
    url(r'^dashboard$', Dashboard.as_view(), name='dashboard'),
    url(r'^robots.txt$', TemplateView.as_view(template_name='core/robots.txt',
                                              content_type='text/plain')),
    url(r'^attribution$', template('core/attribution.html'),
        name='attribution'),
    url(r'^pricing$', PricingView.as_view(), name='pricing'),
    url(r'^privacy$', template('core/privacy.html'), name='privacy'),
    url(r'^tos$', template('core/tos.html'), name='tos'),
    url(r'^contact$', ContactView.as_view(), name='contact'),

    url(r'^blog$', template('blog/index.html'), name='blog'),
    url(r'^blog/feed.xml$', template('blog/feed.xml'), name='feed'),
    url(r'^blog/(?P<article_name>[a-z0-9\-]+)$', ArticleView.as_view()),

    url(r'^account/$', PortalView.as_view(), name='account_portal'),
    url(r'^account/settings$', PortalView.as_view(), name='portal'),
    url(r'^account/plans$', user_redirect, name='upgrade'),
    url(r'^account/plans/pay$', user_redirect, name='pay'),
    url(r'^account/plans/changeplan$', user_redirect, name='changeplan'),
    url(r'^users/[a-zA-Z0-9_]+/?', 'core.views.feed_redirect'),

    url(r'^houston/', include(admin.site.urls)),

)
