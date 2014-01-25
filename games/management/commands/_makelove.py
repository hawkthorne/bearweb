import zipfile

from django.core.management.base import BaseCommand

from games import models, bundle


def package_love(stdout, game, release):
    if release.get_asset('love') is not None:
        stdout.write(u"SKIPPING {}".format(release))
        return

    upload = release.get_asset('uploaded')

    if upload is None:
        stdout.write(u"NO UPLOAD {}".format(release))
        return

    try:
        identity = bundle.detect_identity(upload.blob) or game.slug
    except zipfile.BadZipfile:
        stdout.write(u"BAD ZIP {}".format(release))
        return

    config = bundle.game_config(game.uuid, identity, release.version)

    prefix = "build/love8"

    if release.love_version == "0.9.0":
        prefix = "build/love9"

    # Detect version, fail if not specified
    love = bundle.inject_code(game, upload.blob, config)

    slug = game.slug
    name = game.name

    # Create binaries
    love_file = bundle.blobify(bundle.package_love, game, love, prefix,
                               name, slug, release.version)

    release.add_asset(love_file, tag='love')
    stdout.write(u"FINISHED {}".format(release))


class Command(BaseCommand):
    help = 'Backfill LOVE files for all games'

    def handle(self, *args, **options):

        for game in models.Game.objects.all():
            for release in game.release_set.all():
                package_love(self.stdout, game, release)
