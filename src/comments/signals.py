from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from src.comments.models import Comment
from src.notifications.models import Notification


@receiver(post_save, sender=Comment)
def send_notification(sender, instance, created, **kwargs):
    """create notification object if comment not root and user reply's not his own"""
    parent = instance.get_parent()
    if parent:
        if instance.deleted:
            Notification.objects.filter(
                recipient=instance.reply_to, post=parent.post, parent_comment=parent
            ).delete()

        else:
            if not instance.own_reply and not parent.deleted:
                reply_dtime = instance.created_at.strftime("%A %d %b %Y %H:%M")
                if instance.edited:
                    trans = _("отредактировал(а) ответ на ваш комментарий к ")
                else:
                    trans = _("ответил(а) на ваш комментарий к ")
                text = format_html(
                    "<b>{}</b> {} {} <b>{}</b>.",
                    instance.user,
                    trans,
                    parent.post.title,
                    reply_dtime,
                )
                Notification.objects.create(
                    recipient=instance.reply_to,
                    text=text,
                    post=parent.post,
                    parent_comment=parent,
                )
