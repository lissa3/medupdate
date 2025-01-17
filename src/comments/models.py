import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _
from treebeard.mp_tree import MP_Node

from src.core.models import TimeStamp
from src.posts.models.post_model import Post

User = get_user_model()


class Comment(MP_Node, TimeStamp):
    """
    Auth users can leave a comment (crud) limit chars; UI - htmx
    """

    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="comments")
    body = models.CharField(max_length=2000)
    banned = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)
    edited = models.BooleanField(default=False)
    reply_to = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.DO_NOTHING,
        related_name="reply_ers",
    )
    own_reply = models.BooleanField(default=False)

    class Meta:
        ordering = ("path",)

    @property
    def mark_edited(self):
        return self.created_at != self.updated_at

    @property
    def depth_limit(self):
        """help for UI rendering: nested depth limit for indentaion to left"""
        return self.depth < 2

    def __str__(self):
        return f"{self.user}: {self.body} "
