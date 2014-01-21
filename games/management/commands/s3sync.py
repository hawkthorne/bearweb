import boto
from boto.s3.connection import S3Connection
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Sync old S3 bucket to new S3 bucket'

    def handle(self, *args, **options):
        conn = S3Connection(settings.AWS_ACCESS_KEY_ID,
                            settings.AWS_SECRET_ACCESS_KEY)
        source = conn.get_bucket(settings.AWS_STORAGE_BUCKET_NAME)
        target = conn.get_bucket(settings.AWS_STORAGE_BUCKET_NEW)

        for idx, entry in enumerate(source.list()):
            if entry.name.endswith("/"):
                continue
            if not target.get_key(entry.name):
                self.stdout.write('COPY {}'.format(entry.name))
                try:
                    target.copy_key(entry.name,
                                    settings.AWS_STORAGE_BUCKET_NAME,
                                    entry.name)
                except boto.exception.S3ResponseError, e:
                    self.stderr.write('ERROR {}'.format(e))
            else:
                self.stdout.write('DONE {}'.format(entry.name))
