from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.signals import post_save

from core import tasks


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    plan = models.CharField(max_length=64, default='free')
    stripe_id = models.CharField(max_length=64, default='')


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile, created = UserProfile.objects.get_or_create(user=instance)
        tasks.identify.delay(instance.pk)
        tasks.track.delay(instance.pk, 'Sign Up',
                          distinct_id=instance.username)

post_save.connect(create_user_profile, sender=User)
