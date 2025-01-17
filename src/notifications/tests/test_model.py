from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from src.accounts.tests.factories import UserFactory
from src.comments.models import Comment
from src.notifications.models import Notification
from src.posts.tests.factories import PostFactory


@override_settings(LANGUAGE_CODE="en", LANGUAGES=(("en", "English"),))
class NotificationsMenuTestCase(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.user = UserFactory(username="tata")
        self.author_comment = UserFactory(username="sally")
        self.post = PostFactory.create(
            status=2,
        )
        self.comment = Comment.add_root(
            post=self.post, user=self.author_comment, body="it's me, root comment"
        )

    def test_count_unread_comms(self):
        """test manager Notification"""
        self.client.force_login(self.user)
        # create 5 comments on root comment
        [
            self.comment.add_child(
                post=self.post, body="bar", user=self.user, reply_to=self.author_comment
            )
            for _ in range(5)  # noqa
        ]
        url = reverse("home")
        headers = {"HTTP_HX-Request": "true"}

        resp = self.client.get(url, **headers)

        all_notifs_count = Notification.objects.all_notifics(
            recipient=self.author_comment
        ).count()
        notif_unread_count = Notification.objects.count_unread_notifics(
            recipient=self.author_comment
        )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(all_notifs_count, 5)
        self.assertEqual(notif_unread_count, 5)
