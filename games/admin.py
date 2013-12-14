from django.contrib import admin

from .models import Game, Framework, Release, Asset
from games import tasks


def make_published(modeladmin, request, queryset):
    tasks.error.delay()
make_published.short_description = "This causes an error"


class GameAdmin(admin.ModelAdmin):
    pass


class FrameworkAdmin(admin.ModelAdmin):
    pass


class ReleaseAdmin(admin.ModelAdmin):
    pass


class AssetAdmin(admin.ModelAdmin):
    list_display = ['__unicode__', 'release']
    actions = [make_published]


admin.site.register(Game, GameAdmin)
admin.site.register(Release, ReleaseAdmin)
admin.site.register(Framework, FrameworkAdmin)
admin.site.register(Asset, AssetAdmin)
