import binascii
import hashlib
import os
import re
from urlparse import urlparse

from django.db import models
from django.conf import settings

from subdomains.utils import reverse
from PIL import Image, ImageDraw


def tubeid():
    """Return an 11 character identifier. Does not guaruntee uniqueness"""
    return binascii.hexlify(os.urandom(12))


class Framework(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=128)

    def __unicode__(self):
        return self.name

_PUBLIC_CHOICES = ((True, 'Public'), (False, 'Private'))
_PUBLIC_HELP = "Public games can be downloaded for free without paying"


def icon_path(game, filename):
    return os.path.join(game.uuid, 'images', 'icon.png')


def icns_path(game, filename):
    return os.path.join(game.uuid, 'images', 'icon.icns')


def splash_path(game, filename):
    _, ext = os.path.splitext(filename)
    return os.path.join(game.uuid, 'images', 'splash' + ext)


class Game(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL)
    name = models.CharField(max_length=128)
    slug = models.SlugField(max_length=128)
    uuid = models.CharField(max_length=24, db_index=True, unique=True)
    framework = models.ForeignKey(Framework)
    public = models.BooleanField(default=False, help_text=_PUBLIC_HELP,
                                 choices=_PUBLIC_CHOICES)
    icns = models.ImageField(upload_to=icns_path, null=True, blank=True)
    icon = models.ImageField(upload_to=icon_path, null=True, blank=True)
    splash = models.ImageField(upload_to=splash_path, null=True, blank=True)

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.uuid:
            self.uuid = tubeid()
        super(Game, self).save(*args, **kwargs)

    def download_links(self):
        def fullurl(uuid, platform):
            # FIXME: Make this link SSL
            return reverse('download', args=[uuid, platform])

        return [
            ('Windows', fullurl(self.uuid, 'windows')),
            ('OSX', fullurl(self.uuid, 'osx')),
            ('.love', fullurl(self.uuid, 'love')),
        ]

    def icon_url(self):
        if self.icon:
            return self.icon.url

        url = reverse("identicon", kwargs={"uuid": self.uuid})

        if not settings.DEBUG:
            return settings.STATIC_HOST + urlparse(url).path

        return url

    def identicon(self, size):
        im = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(im)

        digest = hashlib.md5(self.uuid).hexdigest()

        icon = digest[:28]
        hex_color = digest[26:]
        color = (int(hex_color[:2], 16),
                 int(hex_color[2:4], 16),
                 int(hex_color[4:6], 16))
        step = size / 7

        for i, value in enumerate(icon):
            if int(value, 16) % 2 == 0:
                x = (i % 4) * step
                z = (6 - (i % 4)) * step
                y = (i / 4) * step
                draw.rectangle([z, y, z + step - 1, y + step - 1], fill=color)
                draw.rectangle([x, y, x + step - 1, y + step - 1], fill=color)

        del draw  # I'm done drawing so I don't need this anymore

        return im

    def appcast(self):
        items = []

        try:
            release = self.release_set.order_by('-created')[0]
            items.append(release.appcast())
        except IndexError:
            pass

        return {
            'description': 'Eventually put game description here',
            'items': items,
        }

    def latest_release(self):
        return self.release_set.order_by('-created')[0]

    def get_absolute_url(self):
        return reverse("games:view", subdomain='manage',
                       kwargs={"uuid": self.uuid})

    def valid_version(self, new_version):
        """Make sure that the new version is a valid version and
        greater than the current version of the game
        """
        if not re.match(r"\d+\.\d+\.\d+", new_version):
            return False

        x1, y1, z1 = [int(i) for i in self.current_version().split(".")]
        x2, y2, z2 = [int(i) for i in new_version.split(".")]

        if x2 < x1:
            return False

        if x2 == x1 and y2 < y1:
            return False

        if x2 == x1 and y2 == y1 and z2 <= z1:
            return False

        return True

    def current_version(self):
        """If the game has no releases, return 0.1.0. If the game does have a
        release, return the next minor version.
        """
        try:
            return self.release_set.order_by('-created')[0].version
        except IndexError:
            return "0.0.0"

    def next_version(self):
        """If the game has no releases, return 0.1.0. If the game does have a
        release, return the next minor version.
        """
        try:
            release = self.release_set.order_by('-created')[0]
        except IndexError:
            return "0.1.0"

        major, minor, bugfix = release.version.split(".")

        return "{}.{}.{}".format(major, int(minor) + 1, bugfix)

    class Meta:
        unique_together = ("owner", "slug")


class Release(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    game = models.ForeignKey(Game)
    version = models.CharField(max_length=14)
    love_version = models.CharField(max_length=14, default="0.8.0")
    uuid = models.CharField(max_length=24, db_index=True, unique=True)

    def save(self, *args, **kwargs):
        if not self.uuid:
            self.uuid = tubeid()
        super(Release, self).save(*args, **kwargs)

    class Meta:
        unique_together = ("game", "version")

    def add_asset(self, django_file, tag=''):
        return self.asset_set.create(tag=tag, blob=django_file)

    def windows_url(self):
        return self.get_asset_url('windows')

    def osx_url(self):
        return self.get_asset_url('osx')

    def love_url(self):
        return self.get_asset_url('love')

    def appcast(self):
        osx_asset = self.get_asset('osx')
        exe_asset = self.get_asset('exe')
        love_file = self.get_asset('love')

        platforms = []

        if osx_asset:
            platforms.append({
                'name': 'macosx',
                'arch': 'universal',
                'files': [osx_asset.appcast()],
            })

        if love_file:
            platforms.append({
                'name': 'crossplatform',
                'arch': '',
                'files': [love_file.appcast()],
            })

        if exe_asset:
            platforms.append({
                'name': 'windows',
                'arch': 'i386',
                'files': [exe_asset.appcast()],
            })

        return {
            'changelog': '',
            'platforms': platforms,
            'published': '',
            'title': u"{} | Version {}".format(self.game.name, self.version),
            'version': self.version,
        }

    def get_asset(self, tag):
        # FIXME: This will fail if there are other uploaded files
        try:
            return self.asset_set.filter(tag=tag)[0]
        except IndexError:
            return None

    def get_asset_url(self, tag):
        asset = self.get_asset(tag)

        if asset is None:
            return ""

        return asset.blob.url

    def __unicode__(self):
        return u"{} {}".format(self.game.name, self.version)


def asset_path(asset, filename):
    return os.path.join(asset.release.game.uuid,
                        asset.release.version, filename)


class Asset(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    release = models.ForeignKey(Release)
    blob = models.FileField(upload_to=asset_path, max_length=200)
    tag = models.CharField(max_length=20)

    def appcast(self):
        return {
            'url': self.blob.url.replace("https://", "http://"),
            'length': self.blob.size,
        }

    def __unicode__(self):
        return self.blob.name


class CrashReport(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    game = models.ForeignKey(Game)
    traceback = models.TextField()
    # Eventually switch to hstore
    distinct_id = models.CharField(max_length=24, default='')
    version = models.CharField(max_length=14, default='')
    os = models.CharField(max_length=14, default='')
    uuid = models.CharField(max_length=24, db_index=True, unique=True)

    def save(self, *args, **kwargs):
        if not self.uuid:
            self.uuid = tubeid()
        super(CrashReport, self).save(*args, **kwargs)
