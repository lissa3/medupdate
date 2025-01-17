import logging
from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from src.notifications.models import Notification
from src.profiles.models import Profile

User = get_user_model()

logger = logging.getLogger("user_action")


@receiver(post_save, sender=User)
def make_banned_notification(sender, instance, created, *args, **kwargs):
    """top menu contains separate admin notification when user banned"""
    try:
        if instance.banned:
            date_now = date.today()
            tdelta = timedelta(days=14)
            two_wks = date_now + tdelta
            html_2wks = two_wks.strftime("%A %d %b %Y")
            msg = _("Unfortunately your account is temporary banned ")
            admin_word = _("Admin message")
            _till = _("till")
            text = format_html(
                "<p class='red'><b>{}</b></p> {} {} {}",
                admin_word,
                msg,
                _till,
                html_2wks,
            )
            Notification.objects.create(recipient=instance, text=text, from_admin=True)
            profile = Profile.objects.get(user=instance)
            profile.start_ban = date_now
            profile.end_ban = two_wks
            profile.admin_info = "Banned"
            profile.save()
            logger.warning(f"user banned {profile.id}")
    except Exception as e:
        msg = f"Failed to send ban notification {e}"
        logger.warning(msg)
