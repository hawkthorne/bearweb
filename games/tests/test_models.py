from django.test import TestCase

from django.contrib.auth.models import User
from games.models import Game, Framework


class GamesModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user("foo", "bar@example.com", "pass")
        self.other = Framework.objects.create(name="Other")

    def test_game_first_release(self):
        game = Game.objects.create(owner=self.user, framework=self.other,
                                   name="Foo", slug="foo")
        self.assertEquals("1.0.0", game.next_version())

    def test_game_next_release(self):
        game = Game.objects.create(owner=self.user, framework=self.other,
                                   name="Foo", slug="foo")
        game.release_set.create(version="1.0.0")

        self.assertEquals("2.0.0", game.next_version())
