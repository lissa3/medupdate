import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.shortcuts import reverse
from django.utils.translation import gettext_lazy as _

from src.core.models import TimeStamp
from src.core.utils.base import upload_img
from src.core.utils.magic_valid_files import validate_img_mimetype
from src.profiles.managers import ProfileManager

User = get_user_model()


class Profile(TimeStamp):
    """
    In OneToOne relation with User Model
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)  # ?PROTECT
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    avatar = models.ImageField(
        _("Avatar"),
        upload_to=upload_img,
        blank=True,
        null=True,
        validators=[validate_img_mimetype],
    )
    admin_info = models.CharField(max_length=120, default="", blank=True)
    want_news = models.BooleanField(default=False, blank=True)
    start_ban = models.DateField(null=True, blank=True)
    end_ban = models.DateField(null=True, blank=True)
    objects = ProfileManager.as_manager()

    def get_absolute_url(self):
        return reverse("profiles:profile_detail", kwargs={"uuid": self.uuid})

    def delete(self):
        """if profile obj deleted; remove avatar file"""
        self.avatar.delete()
        super().delete()

    def __str__(self) -> str:
        return self.user.username


class ProfileChart(Profile):
    """show in graph profile obj creation"""

    class Meta:
        proxy = True
