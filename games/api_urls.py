from django.conf.urls import patterns, url

from .api import metrics, errors, appcast

urlpatterns = patterns(
    '',
    url(r'^games/([0-9a-f]{24})/metrics$', metrics),
    url(r'^games/([0-9a-f]{24})/errors$', errors),
    url(r'^games/([0-9a-f]{24})/appcast$', appcast),
)
