from django.contrib.auth.signals import user_logged_in, user_logged_out
from core import tasks


def track_login(sender, user, request, **kwargs):
    tasks.track.delay('Sign In', distinct_id=request.user.username)


def track_logout(sender, user, request, **kwargs):
    tasks.track.delay('Sign Out', distinct_id=request.user.username)


def connect():
    user_logged_in.connect(track_login)
    user_logged_out.connect(track_logout)
