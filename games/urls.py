from django.conf.urls import patterns, url

from .views import GameCreate, GameDetail, ReleaseList, ReleaseCreate

urlpatterns = patterns(
    '',
    url(r'^new$', GameCreate.as_view(), name='create'),
    url(r'^(?P<pk>\d+)$', GameDetail.as_view(), name='view'),
    url(r'^(?P<pk>\d+)/metrics$', GameDetail.as_view(), name='metrics'),
    url(r'^(?P<pk>\d+)/releases$', ReleaseList.as_view(), name='releases'),
    url(r'^(?P<pk>\d+)/releases/new$', ReleaseCreate.as_view(),
        name='newrelease'),
    url(r'^(?P<pk>\d+)/crashes$', GameDetail.as_view(), name='crashes'),
)
