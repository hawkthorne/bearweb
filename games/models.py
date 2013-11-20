from django.core.urlresolvers import reverse
from django.db import models
from django.conf import settings


class Framework(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=128)

    def __unicode__(self):
        return self.name


class Game(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL)
    name = models.CharField(max_length=128)
    slug = models.SlugField(max_length=128, db_index=True)
    framework = models.ForeignKey(Framework)

    def get_absolute_url(self):
        return reverse("games:view", pk=self.pk)

    def next_version(self):
        """If the game has no releases, return 1.0.0. If the game does have a
        release, return the next major version.
        """
        try:
            release = self.release_set.order_by('created')[0]
        except IndexError:
            return "1.0.0"

        major, minor, bugfix = release.version.split(".")

        return "{}.{}.{}".format(int(major) + 1, minor, bugfix)

    class Meta:
        unique_together = ("owner", "slug")


class Release(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    game = models.ForeignKey(Game)
    version = models.CharField(max_length=14)
    original_file = models.FileField(upload_to='games')


class Asset(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    release = models.ForeignKey(Release)
    filename = models.CharField(max_length=64)


class CrashReport(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    game = models.ForeignKey(Game)
    traceback = models.TextField()
    # Think about using json for this
    # distinct_id = models.CharField()
    # version = models.CharField()
    # os = models.CharField()
