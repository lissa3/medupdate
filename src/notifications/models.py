from django.contrib.auth import get_user_model
from django.db import models
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from src.comments.models import Comment
from src.posts.models.post_model import Post

User = get_user_model()


class NotificationManager(models.Manager):
    def get_queryset(self):
        return (
            super().get_queryset().select_related("recipient", "post", "parent_comment")
        )

    def all_notifics(self, recipient):
        return self.get_queryset().filter(recipient=recipient)

    def all_unread_notifics(self, recipient):
        """count unread notifs: admin + comments replies"""
        return self.get_queryset().filter(recipient=recipient, read=False)

    def make_all_read(self, recipient):
        """exclude admin msg and filter unread notifs  convert them to read"""
        qs = (
            self.get_queryset()
            .exclude(from_admin=True)
            .filter(recipient=recipient, read=False)
        )
        qs.update(read=True)

    def count_unread_notifics(self, recipient):
        """filter qs without admin msg"""
        return (
            self.get_queryset()
            .exclude(from_admin=True)
            .filter(recipient=recipient, read=False)
            .count()
        )

    def get_top(self, recipient):
        # exclude admin msg (ban)
        clear_admin = self.get_queryset().exclude(from_admin=True)
        return clear_admin.filter(recipient=recipient, read=False)[:5]


class Notification(models.Model):
    created = models.DateTimeField(default=now)
    recipient = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    read = models.BooleanField(default=False)
    from_admin = models.BooleanField(default=False)
    post = models.ForeignKey(Post, null=True, blank=True, on_delete=models.CASCADE)
    parent_comment = models.ForeignKey(
        Comment, null=True, blank=True, on_delete=models.SET_NULL
    )

    objects = NotificationManager()

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return f"Notification for {self.recipient} | id={self.id}"
