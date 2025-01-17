# from contextlib import contextmanager
from unittest.mock import Mock

from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.test import TestCase

from src.accounts.tests.factories import UserFactory
from src.comments.models import Comment
from src.comments.tests.factories import CommentFactory
from src.notifications.models import Notification

User = get_user_model()


class NotificationCreation(TestCase):
    def setUp(self) -> None:
        self.replier = UserFactory(username="sam")
        self.author_root_comment = UserFactory(username="sally")
        self.user_to_ban = UserFactory(username="boze wolf")

    def test_comment_signal(self):
        """notification obj via signal when new child-comment created"""
        handler = Mock()
        post_save.connect(handler, sender=Comment)
        root_comment = CommentFactory()
        root_comment.add_child(
            user=self.replier,
            post=root_comment.post,
            body="low water",
            reply_to=self.author_root_comment,
        )
        notifs_count = Notification.objects.count()

        self.assertTrue(handler.called)
        self.assertEqual(root_comment.get_children().count(), 1)
        self.assertEqual(notifs_count, 1)

    def test_root_comment_signal(self):
        """test no notification via signal when root-comment created"""
        handler = Mock()
        post_save.connect(handler, sender=Comment)
        CommentFactory()
        notifs_count = Notification.objects.count()

        self.assertTrue(handler.called)
        self.assertEqual(notifs_count, 0)

    def test_banned_user_signal(self):
        """notification via signal when user banned"""
        handler = Mock()
        post_save.connect(handler, sender=User)
        self.user_to_ban.banned = True
        self.user_to_ban.save()
        self.user_to_ban.profile.refresh_from_db()
        notifs_count = Notification.objects.count()

        self.assertTrue(handler.called)
        self.assertEqual(notifs_count, 1)
