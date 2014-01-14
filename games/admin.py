from django.contrib import admin

from .models import Game, Framework, Release, Asset


class GameAdmin(admin.ModelAdmin):
    list_display = ['name', 'uuid', 'created', 'owner', 'framework', 'public']


class FrameworkAdmin(admin.ModelAdmin):
    pass


class ReleaseAdmin(admin.ModelAdmin):
    list_display = ['__unicode__', 'created', 'game', 'version']


class AssetAdmin(admin.ModelAdmin):
    list_display = ['__unicode__', 'release']

admin.site.register(Game, GameAdmin)
admin.site.register(Release, ReleaseAdmin)
admin.site.register(Framework, FrameworkAdmin)
admin.site.register(Asset, AssetAdmin)
