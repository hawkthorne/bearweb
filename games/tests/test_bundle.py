# -*- coding: utf-8 -*-
import zipfile
import os
import unittest
import shutil

from django.test import TestCase
from django.core.files import File
from django.contrib.auth.models import User
from django.conf import settings
from zipfile import ZipFile

from games.models import Game, Framework
from games import bundle


def simple_love():
    love = zipfile.ZipFile('test.love', 'w')
    contents = 'function love.draw() love.graphics.print("HELLO", 0, 0) end'
    love.writestr('main.lua', contents)
    love.close()
    return File(open('test.love'))


LOVE_9_CONF = u"""
function love.conf(t)
    t.identity = "Picaro" -- The name of the save directory (string)
    t.version = "0.9.0"   -- The LÖVE version this game was made for (string)
    t.console = false     -- Attach a console (boolean, Windows only)
end
"""

LOVE_9_CONF_TICK = u"""
function love.conf(t)
    t.identity = "Picaro" -- The name of the save directory (string)
    t.version = '0.9.0'   -- The LÖVE version this game was made for (string)
    t.console = false     -- Attach a console (boolean, Windows only)
end
"""

LOVE_8_CONF = u"""
function love.conf(t)
    t.identity = "Picaro" -- The name of the save directory (string)
    t.version = "0.8.0"   -- The LÖVE version this game was made for (string)
    t.console = false     -- Attach a console (boolean, Windows only)
end
"""

LOVE_NO_CONF = u"""
function love.conf(t)
    t.identity = "Picaro" -- The name of the save directory (string)
    t.console = false     -- Attach a console (boolean, Windows only)
end
"""


class BundleTests(TestCase):

    def test_relpath(self):
        path = os.path.join(settings.SITE_ROOT, "games", "build",
                            "osx", "love.app", "Contents")

        newpath = bundle.relpath(path, "foo.app")
        self.assertEquals("foo.app/Contents", newpath)

    def test_detect_love9(self):
        self.assertEquals("0.9.0", bundle.love_version(LOVE_9_CONF))

    def test_detect_love9_tick(self):
        self.assertEquals("0.9.0", bundle.love_version(LOVE_9_CONF_TICK))

    def test_detect_love8(self):
        self.assertEquals("0.8.0", bundle.love_version(LOVE_8_CONF))

    def test_detect_no_version(self):
        self.assertEquals(None, bundle.love_version(LOVE_NO_CONF))


class GamesModelTests(TestCase):

    def setUp(self):
        try:
            shutil.rmtree('media')
        except OSError:
            pass

        self.user = User.objects.create_user("foo", "bar@example.com", "pass")
        self.other = Framework.objects.create(name="Other")
        self.game = Game.objects.create(owner=self.user, framework=self.other,
                                        name="foo", slug="foo")

    @unittest.skipIf('DISABLE_SLOW' in os.environ, "This is a slow test")
    def test_package_simple_game(self):
        release = self.game.release_set.create(version="0.1.0")
        release.asset_set.create(blob=simple_love(), tag='uploaded')

        bundle.package(release.pk)

        asset = release.get_asset('osx')

        self.assertIn('0.1.0/foo-osx-0.1.0.zip', asset.blob.url)

    def test_package_game_with_folders(self):
        os.mkdir('media')

        lovefile = os.path.abspath('games/tests/game_with_folders.love')
        path = bundle.inject_code(lovefile, "{}")

        shutil.move(path, 'media/game.love')

        oldzip = ZipFile(lovefile)
        newzip = ZipFile('media/game.love')

        newperm = newzip.getinfo('foo/').external_attr
        oldperm = oldzip.getinfo('foo/').external_attr
        self.assertEquals(oldperm, newperm)

        newperm = newzip.getinfo('foo/bar.lua').external_attr
        oldperm = oldzip.getinfo('foo/bar.lua').external_attr
        self.assertEquals(oldperm, newperm)
