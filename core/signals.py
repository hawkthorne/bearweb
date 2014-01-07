from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver

from core import tasks


@receiver(user_logged_in)
def track_login(sender, user, request, **kwargs):
    tasks.track.delay(user.pk, 'Sign In', distinct_id=request.user.username)


@receiver(user_logged_out)
def track_logout(sender, user, request, **kwargs):
    tasks.track.delay(user.pk, 'Sign Out', distinct_id=request.user.username)
