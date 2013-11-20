from django.contrib import admin

from .models import Game, Framework, Release, Asset


class GameAdmin(admin.ModelAdmin):
    pass


class FrameworkAdmin(admin.ModelAdmin):
    pass


class ReleaseAdmin(admin.ModelAdmin):
    pass


class AssetAdmin(admin.ModelAdmin):
    pass


admin.site.register(Game, GameAdmin)
admin.site.register(Release, ReleaseAdmin)
admin.site.register(Framework, FrameworkAdmin)
admin.site.register(Asset, AssetAdmin)
