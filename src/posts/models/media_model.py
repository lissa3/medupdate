# from django.core.files.storage import FileSystemStorage
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from embed_video.fields import EmbedVideoField

from src.core.models import MediaStamp
from src.core.utils.base import upload_img


class Video(MediaStamp):
    class ImageCategory(models.IntegerChoices):
        SINGLE = 0, _("first")
        GENERAL = 1, _("general")
        ENDO = 2, _("endo")
        CARDIO = 3, _("cardio")
        GI = 4, _("gastro")
        IMMUN = 5, _("immune")
        URO = 6, _("uro_gen")
        NEURO = 7, _("neuro")
        TOXI = 8, _("toxic")
        GERON = 9, _("geron")
        __empty__ = _("(Unknown)")

    url = EmbedVideoField()
    title = models.CharField(max_length=120, default="", blank=True)
    # check obj.EMBED_VIDEO_YOUTUBE_CHECK_THUMBNAIL
    thumbnail = models.ImageField(upload_to=upload_img, null=True, blank=True)
    categ = models.IntegerField(
        choices=ImageCategory.choices, default=ImageCategory.GENERAL
    )

    def save(self, *args, **kwargs):
        """auto create datetime if public status changes"""
        self.created = timezone.now().date()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"id {self.id}"


class ImageCollection(models.Model):
    class ImageCategory(models.IntegerChoices):
        GENERAL = 0, _("general")
        KNO = 1, _("kno")
        ENDO = 2, _("endo")
        CARDIO = 3, _("cardio")
        GI = 4, _("gastro")
        IMMUN = 5, _("immune")
        URO = 6, _("uro_gen")
        NEURO = 7, _("neuro")
        TOXI = 8, _("toxic")
        GERON = 9, _("geron")
        __empty__ = _("(Unknown)")

    pic = models.ImageField(upload_to=upload_img)
    title = models.CharField(max_length=250, default="", blank=True)
    bron = models.URLField(default="", blank=True)
    categ = models.IntegerField(
        choices=ImageCategory.choices, default=ImageCategory.GENERAL
    )

    def __str__(self) -> str:
        return f"{self.id}"
