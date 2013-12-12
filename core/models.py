from django.db import models
from django.conf import settings
from django.db.models.signals import post_save


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    plan = models.CharField(max_length=64, default='free')
    stripe_id = models.CharField(max_length=64, default='')


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile, created = UserProfile.objects.get_or_create(user=instance)

post_save.connect(create_user_profile, sender=settings.AUTH_USER_MODEL)
