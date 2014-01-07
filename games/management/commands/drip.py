from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.contrib.auth.models import User

from games.models import Game
from customerio import CustomerIO

class Command(BaseCommand):
    help = 'Sync current state into Customer IO'

    def handle(self, *args, **options):
        cio = CustomerIO(settings.CUSTOMERIO_SITE_ID,
                         settings.CUSTOMERIO_API_KEY)

        for user in User.objects.all():
            cio.identify(id=user.pk, email=user.email, username=user.username)
            self.stdout.write('IDENTIFY {}'.format(user.username))

        for game in Game.objects.all():
            pk = game.owner.pk

            cio.track(customer_id=pk, name='Create Game', game=game.slug)
            self.stdout.write('TRACK Game {}'.format(game.slug))

            for release in game.release_set.all():
                cio.track(customer_id=pk, name='Create Release',
                          game=game.slug, version=release.version)
                self.stdout.write('TRACK Release {}'.format(release.version))


