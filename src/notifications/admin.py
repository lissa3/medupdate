from django.contrib import admin

from src.notifications.models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """display notifications list"""

    list_display = ("id", "recipient", "read", "text", "post_id")
    list_filter = ("created", "recipient")
    list_display_links = ["recipient"]
    date_hierarchy = "created"
