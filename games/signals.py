from django.dispatch import receiver
from django.db.models.signals import post_save

from core import tasks
from games import models


@receiver(post_save, sender=models.Release)
def track_create_release(sender, instance, created, **kwargs):
    if created:
        tasks.track.delay(instance.game.owner.pk, 'Create Release',
                          game=instance.game.slug,
                          distinct_id=instance.game.owner.username)


@receiver(post_save, sender=models.Game)
def track_create_game(sender, instance, created, **kwargs):
    if created:
        tasks.track.delay(instance.owner.pk, 'Create Game',
                          game=instance.slug,
                          distinct_id=instance.owner.username)
