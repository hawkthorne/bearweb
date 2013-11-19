from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from core.views import ContactView, PortalView, PricingView, GuideView
from core.views import HomeView, RepositoryDelete, RepositoryView
from core.views import UpgradeView, UpgradePayView, ChangePlanView
from core.views import AccessTokenView, AccessTokenCreate
from blog.views import ArticleView


def template(path):
    return TemplateView.as_view(template_name=path)


rlpatterns = patterns(
    '',
    url(r'', include('social_auth.urls')),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout',
        {'next_page': '/'}),
    url(r'^accounts/', include('registration.backends.simple.urls')),
    url(r'^$', HomeView.as_view(), name='home'),
    url(r'^robots.txt$', TemplateView.as_view(template_name='core/robots.txt',
                                              content_type='text/plain')),
    url(r'^pricing$', PricingView.as_view(), name='pricing'),
    url(r'^privacy$', template('core/privacy.html'), name='privacy'),
    url(r'^tos$', template('core/tos.html'), name='tos'),
    url(r'^contact$', ContactView.as_view(), name='contact'),

    url(r'^guide$', GuideView.as_view(), name='guide'),

    url(r'^blog$', template('blog/index.html'), name='blog'),
    url(r'^blog/feed.xml$', template('blog/feed.xml'), name='feed'),
    url(r'^blog/(?P<article_name>[a-z0-9\-]+)$', ArticleView.as_view()),

    url(r'^account/$', PortalView.as_view(), name='account_portal'),
    url(r'^account/settings$', PortalView.as_view(), name='portal'),
    url(r'^account/tokens$', AccessTokenView.as_view(), name='tokens'),
    url(r'^account/tokens/create$', AccessTokenCreate.as_view(),
        name='tokens_create'),
    url(r'^account/plans$', UpgradeView.as_view(), name='upgrade'),
    url(r'^account/plans/pay$', UpgradePayView.as_view(), name='pay'),
    url(r'^account/plans/changeplan$',
        ChangePlanView.as_view(), name='changeplan'),
    url(r'^users/[a-zA-Z0-9_]+/?', 'core.views.user_redirect'),

    url(r'^houston/', include(admin.site.urls)),
)
