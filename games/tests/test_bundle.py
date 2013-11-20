import zipfile

from django.test import TestCase
from django.core.files import File
from django.contrib.auth.models import User

from games.models import Game, Framework
from games import bundle


def simple_love():
    love = zipfile.ZipFile('test.love', 'w')
    contents = 'function love.draw() love.graphics.print("HELLO", 0, 0) end'
    love.writestr('main.lua', contents)
    love.close()
    return File(open('test.love'))


class GamesModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user("foo", "bar@example.com", "pass")
        self.other = Framework.objects.create(name="Other")
        self.game = Game.objects.create(owner=self.user, framework=self.other,
                                        name="foo", slug="foo")

    def test_package_simple_game(self):
        release = self.game.release_set.create(version="1.0.0",
                                               original_file=simple_love())
        bundle.package(release.pk)
