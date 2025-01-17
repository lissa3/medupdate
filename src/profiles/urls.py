from django.urls import path

from .views import ProfileDelete, ProfileView

app_name = "profiles"

urlpatterns = [
    path("<uuid:uuid>/", ProfileView.as_view(), name="profile_detail"),
    path("delete/<uuid:uuid>/", ProfileDelete.as_view(), name="profile_delete"),
]
