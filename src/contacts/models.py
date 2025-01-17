from django.db import models
from django.utils.translation import gettext_lazy as _

from src.core.models import MediaStamp


class NewsLetter(MediaStamp):
    """
    title/text: empty string default
    post can be NULL (letter without post link)
    TODO:ask to help with translations;
    """

    class Status(models.IntegerChoices):
        PENDING = 0, _("pending")
        READY = 1, _("ready to send")
        SENT = 2, _("sent")

    text = models.TextField(default="", blank=True)
    letter_status = models.IntegerField(
        choices=Status.choices, default=Status.PENDING, blank=True
    )
    date_sent = models.DateField(null=True, blank=True)

    def __str__(self) -> str:
        return f"#id: {self.id} - {self.letter_status}"
