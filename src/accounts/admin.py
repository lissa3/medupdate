# Register your models here.
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserChangeForm

from .forms import UserCreationForm

User = get_user_model()


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """based on AbstractUser model"""

    search_fields = ("email", "username")
    add_form = UserCreationForm
    form = UserChangeForm
    list_display = (
        "username",
        "banned",
        "email",
        "last_login",
        "is_staff",
        "is_active",
        "is_superuser",
        "id",
    )
    list_display_links = ["username", "email"]
    readonly_fields = ["last_login", "date_joined"]
    list_filter = ("is_active", "is_superuser", "is_staff")
    add_fieldsets = (
        (
            ("Add Your User"),
            {
                "classes": ("wide",),
                "fields": ("username", "email", "password1", "password2"),
            },
        ),
    )
    fieldsets = (
        (
            ("Main"),
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "email",
                    "banned",
                    "is_active",
                    "deactivated_on",
                    "blackListEmail",
                    "groups",
                    "is_staff",
                ),
            },
        ),
    )
