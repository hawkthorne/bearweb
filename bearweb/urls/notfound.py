from django.conf.urls import patterns, url
from core.views import LostInSpace

urlpatterns = patterns(
    '',
    url(r'^.*$', LostInSpace.as_view()),
)
