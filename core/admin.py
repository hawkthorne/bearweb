from django.contrib import admin

from core.models import Subscription


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("user", "plan")


admin.site.register(Subscription, SubscriptionAdmin)
