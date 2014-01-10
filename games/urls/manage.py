from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

from ..views import GameCreate, GameDetail, ReleaseList, ReleaseCreate
from ..views import ReportList, download

from core.views import ContactView, PortalView, PricingView
from core.views import Dashboard, user_redirect

def pat(fragment):
    return '(?P<uuid>[0-9a-f]{24})' + fragment + '$'


urlpatterns = patterns(
    '',
    url(r'^users/logout/$', 'django.contrib.auth.views.logout',
        {'next_page': '/'}),
    #url(r'^users/[a-zA-Z0-9_]+/?', 'core.views.feed_redirect'),

    url(r'^$', Dashboard.as_view(), name='dashboard'),
    url(r'^account/$', PortalView.as_view(), name='account_portal'),
    url(r'^account/settings$', PortalView.as_view(), name='portal'),
    url(r'^account/plans$', user_redirect, name='upgrade'),
    url(r'^account/plans/pay$', user_redirect, name='pay'),
    url(r'^account/plans/changeplan$', user_redirect, name='changeplan'),

    url(r'^robots.txt$', TemplateView.as_view(template_name='games/robots.txt',
                                              content_type='text/plain')),

    url(r'^users/', include('registration.backends.simple.urls')),
    url(r'^games/', include('games.urls', namespace='games')),
)
