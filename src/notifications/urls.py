from django.urls import path

from .views import get_top, make_notifs_read, show_unread_notifs

app_name = "notifications"

# all urls for htmx requests
urlpatterns = [
    path("", get_top, name="top_notifics"),
    path("show-notifications/", show_unread_notifs, name="show_notifs"),
    path("make-as-read/<notif_id>/", make_notifs_read, name="admin_read"),
    path("make-as-read/", make_notifs_read, name="mark_read"),
]
