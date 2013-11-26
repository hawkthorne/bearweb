from django.conf.urls import patterns, url

from .api import metrics, errors, appcast

urlpatterns = patterns(
    '',
    url(r'^games/(\d+)/metrics$', metrics),
    url(r'^games/(\d+)/errors$', errors),
    url(r'^games/(\d+)/appcast$', appcast),
)
