from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.base import ContentFile

from games.models import Game, Framework


class GamesModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user("foo", "bar@example.com", "pass")
        self.other = Framework.objects.create(name="Other")

    def test_game_first_release(self):
        game = Game.objects.create(owner=self.user, framework=self.other,
                                   name="Foo", slug="foo")
        self.assertEquals("0.1.0", game.next_version())

    def test_game_next_release(self):
        game = Game.objects.create(owner=self.user, framework=self.other,
                                   name="Foo", slug="foo")
        game.release_set.create(version="0.1.0")
        game.release_set.create(version="0.2.0")

        self.assertEquals("0.3.0", game.next_version())

    def test_release_add_asset(self):
        game = Game.objects.create(owner=self.user, framework=self.other,
                                   name="Foo", slug="foo")
        release = game.release_set.create(version='0.1.0')

        blob = ContentFile('foo')
        blob.name = 'foo.txt'

        asset = release.add_asset(blob)

        self.assertTrue(asset.blob.url.startswith("/media/foo/0.1.0/"))
