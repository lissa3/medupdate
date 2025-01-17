from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    username = models.CharField(max_length=120, unique=True)
    email = models.EmailField(unique=True, max_length=120)
    deactivated_on = models.DateField(
        verbose_name=_("Deactivated on"),
        null=True,
        blank=True,
        help_text=_("This is the date the user deactivated his account."),
    )
    banned = models.BooleanField(default=False)
    blackListEmail = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self) -> str:
        return self.username

    @property
    def display_name(self) -> str:
        return self.username

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
