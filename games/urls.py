from django.conf.urls import patterns, url

from .views import GameCreate

urlpatterns = patterns(
    '',
    url(r'^create', GameCreate.as_view(), name='create'),
)
 
