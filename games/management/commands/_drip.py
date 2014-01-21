from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth.models import User

from customerio import CustomerIO


class Command(BaseCommand):
    help = 'Sync current state into Customer IO'

    def handle(self, *args, **options):
        cio = CustomerIO(settings.CUSTOMERIO_SITE_ID,
                         settings.CUSTOMERIO_API_KEY)

        for user in User.objects.all():
            cio.track(customer_id=user.pk, name='Sign Up')
            self.stdout.write('SIGN UP {}'.format(user.username))
