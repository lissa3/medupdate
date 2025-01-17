from django.db.models import signals
from django.test import TestCase
from factory.django import mute_signals
from freezegun import freeze_time

from src.accounts.tests.factories import UserFactory

from .factories import CommentFactory


class CommentModelTestCase(TestCase):
    def setUp(self) -> None:
        with freeze_time("2023-01-01 01:00:00"):
            self.comment_root = CommentFactory()

    def test_comment_root_attrs(self):
        """check default attrs for root comment_root"""
        self.assertIsNotNone(self.comment_root.body)
        self.assertIsNotNone(self.comment_root.user)
        self.assertIsNotNone(self.comment_root.post)
        self.assertIsNone(self.comment_root.reply_to)
        self.assertFalse(self.comment_root.banned)
        self.assertFalse(self.comment_root.deleted)
        self.assertEqual(self.comment_root.mark_edited, False)
        self.assertEqual(self.comment_root.created_at, self.comment_root.updated_at)

    def test_child_comment(self):
        """add a child comment"""
        self.assertEqual(self.comment_root.get_children().count(), 0)
        reply_er = UserFactory()
        with mute_signals(signals.post_save):
            self.comment_root.add_child(
                user=reply_er,
                post=self.comment_root.post,
                body="reply to the root comment",
            )
        self.assertEqual(self.comment_root.get_children().count(), 1)
