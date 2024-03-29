from django.conf.urls import patterns, url

from .api import metrics, errors, appcast
from .view import download

urlpatterns = patterns(
    '',
    url(r'^games/(?P<uuid>[0-9a-f]{24})/download/(?P<platform>windows|osx)$',
        download, name='download'),
    url(r'^games/([0-9a-f]{24})/metrics$', metrics),
    url(r'^games/([0-9a-f]{24})/errors$', errors),
    url(r'^games/([0-9a-f]{24})/appcast$', appcast),
)
