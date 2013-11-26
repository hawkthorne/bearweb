import zipfile
import os
import unittest
import shutil

from django.test import TestCase
from django.core.files import File
from django.contrib.auth.models import User
from django.conf import settings

from games.models import Game, Framework
from games import bundle


def simple_love():
    love = zipfile.ZipFile('test.love', 'w')
    contents = 'function love.draw() love.graphics.print("HELLO", 0, 0) end'
    love.writestr('main.lua', contents)
    love.close()
    return File(open('test.love'))


class BundleTests(TestCase):

    def test_relpath(self):
        path = os.path.join(settings.SITE_ROOT, "games", "build",
                            "osx", "love.app", "Contents")

        newpath = bundle.relpath(path, "foo.app")
        self.assertEquals("foo.app/Contents", newpath)


class GamesModelTests(TestCase):

    def setUp(self):
        shutil.rmtree('media')
        self.user = User.objects.create_user("foo", "bar@example.com", "pass")
        self.other = Framework.objects.create(name="Other")
        self.game = Game.objects.create(owner=self.user, framework=self.other,
                                        name="foo", slug="foo")

    @unittest.skipIf('DISABLE_SLOW' in os.environ, "This is a slow test")
    def test_package_simple_game(self):
        release = self.game.release_set.create(version="1.0.0")
        release.asset_set.create(blob=simple_love(), tag='uploaded')

        bundle.package(release.pk)

        asset = release.get_asset('osx')

        self.assertIn('foo/1.0.0/foo-osx-1.0.0.zip', asset.blob.url)
