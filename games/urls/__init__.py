from django.conf.urls import patterns, url

from ..views import GameCreate, GameDetail, ReleaseList, ReleaseCreate
from ..views import ReportList, download


def pat(fragment):
    return '(?P<uuid>[0-9a-f]{24})' + fragment + '$'


urlpatterns = patterns(
    '',
    url(r'^new$', GameCreate.as_view(), name='create'),
    url(pat('$'), GameDetail.as_view(), name='view'),
    url(pat('/download/(?P<platform>windows|osx)$'), download,
        name='download'),
    url(pat('/metrics$'), GameDetail.as_view(), name='metrics'),
    url(pat('/releases$'), ReleaseList.as_view(), name='releases'),
    url(pat('/releases/new$'), ReleaseCreate.as_view(),
        name='newrelease'),
    url(pat('/crashes$'), ReportList.as_view(), name='crashes'),
)
