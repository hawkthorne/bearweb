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

CONF = """
function love.conf(t)
  t.version = "{}"
  t.identity = "{}"
end
"""

MAIN = """
function love.draw()
  love.graphics.print(love._version, 0, 0)
end
"""


def create_lovefile(path, name, version):
    love = zipfile.ZipFile(path, 'w')
    love.writestr('main.lua', MAIN)
    contents = CONF.format(version, name)
    love.writestr('conf.lua', contents)
    love.close()
    return love


def simple_love(name, version):
    lovepath = os.path.join('gen', '{}.love'.format(name))
    create_lovefile(lovepath, name, version)
    return File(open(lovepath))

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

    def setUp(self):
        try:
            os.mkdir('gen')
        except OSError:
            pass

    def test_relpath(self):
        path = os.path.join(settings.SITE_ROOT, "games", "build",
                            "love8", "osx", "love.app", "Contents")

        newpath = bundle.relpath("build/love8", path, "foo.app")
        self.assertEquals("foo.app/Contents", newpath)

    def test_detect_love9(self):
        self.assertEquals("0.9.0", bundle.love_version(LOVE_9_CONF))

    def test_detect_love9_tick(self):
        self.assertEquals("0.9.0", bundle.love_version(LOVE_9_CONF_TICK))

    def test_detect_love8(self):
        self.assertEquals("0.8.0", bundle.love_version(LOVE_8_CONF))
        self.assertEquals("Picaro", bundle.love_identity(LOVE_8_CONF))

    def test_detect_no_version(self):
        self.assertEquals(None, bundle.love_version(LOVE_NO_CONF))

    def test_detect_no_version_fixture(self):
        path = 'games/tests/fixtures/no_identity_version.love'
        self.assertEquals(None, bundle.detect_version(path))

    def test_detect_no_identity(self):
        path = 'games/tests/fixtures/no_identity_version.love'
        self.assertEquals(None, bundle.detect_identity(path))

    def test_detect_identity(self):
        path = 'games/tests/fixtures/foobaridentity.love'
        self.assertEquals('foobar', bundle.detect_identity(path))

    def test_detect_missing_files(self):
        path = 'games/tests/fixtures/invalid.love'
        self.assertFalse(bundle.check_for_main(path))

    @unittest.skipIf('DISABLE_SLOW' in os.environ, "This is a slow test")
    def test_lovefile_detect(self):
        create_lovefile('gen/love8.love', 'foo8', '0.8.0')
        self.assertEquals('0.8.0', bundle.detect_version('gen/love8.love'))


class GamesModelTests(TestCase):

    @classmethod
    def setUpClass(cls):
        try:
            shutil.rmtree('media')
        except OSError:
            pass

        os.mkdir('media')

    def setUp(self):
        self.user = User.objects.create_user("foo", "bar@example.com", "pass")
        self.other = Framework.objects.create(name="Other")
        self.game = Game.objects.create(owner=self.user, framework=self.other,
                                        name="foo", slug="foo")

    @unittest.skipIf('DISABLE_SLOW' in os.environ, "This is a slow test")
    def test_package_simple_game_8(self):
        release = self.game.release_set.create(version="0.1.8")
        release.asset_set.create(blob=simple_love('bar8', "0.8.0"),
                                 tag='uploaded')

        bundle.package(release.pk)

        asset = release.get_asset('osx')

        self.assertIn('0.1.8/foo-osx.zip', asset.blob.url)

    @unittest.skipIf('DISABLE_SLOW' in os.environ, "This is a slow test")
    def test_package_simple_game_9(self):
        release = self.game.release_set.create(love_version="0.9.0",
                                               version="0.1.9")
        release.asset_set.create(blob=simple_love('bar9', "0.9.0"),
                                 tag='uploaded')

        bundle.package(release.pk)

        asset = release.get_asset('osx')

        self.assertIn('0.1.9/foo-osx.zip', asset.blob.url)

    def test_package_game_with_folders(self):
        lovefile = os.path.abspath(
            'games/tests/fixtures/game_with_folders.love')
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
