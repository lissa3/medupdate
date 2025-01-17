from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from src.accounts.tests.factories import UserFactory
from src.comments.models import Comment
from src.comments.tests.factories import CommentFactory
from src.contacts.exceptions import HtmxFailureError
from src.notifications.models import Notification
from src.posts.tests.factories import PostFactory


@override_settings(LANGUAGE_CODE="en", LANGUAGES=(("en", "English"),))
class NotificationsFabricTestCase(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.user = UserFactory(username="tata")
        self.author_comment = UserFactory(username="sally")
        self.post = PostFactory.create(
            title_en="Bell's palsy",
            content_en="herpes virus, treatment,prednisone",
            status=2,
        )
        self.comment = Comment.add_root(
            post=self.post, user=self.author_comment, body="it's me, root comment"
        )

    def test_notific_on_reply_comment(self):
        """htmx: adding child comment(reply to a root comment)"""
        self.client.force_login(self.user)
        url = reverse(
            "comments:process_comm",
            kwargs={"post_uuid": self.post.uuid},
        )
        data = {
            "body": "Tata replies Sally",
            "comm_parent_id": self.comment.id,
            "post": self.post,
        }
        headers = {"HTTP_HX-Request": "true"}

        resp = self.client.post(url, data=data, **headers)

        notif_count = Notification.objects.count()
        notif_to_author = Notification.objects.last()

        self.assertEqual(resp.status_code, 204)
        self.assertFalse(notif_to_author.read)
        self.assertEqual(notif_to_author.post, self.post)
        self.assertEqual(notif_to_author.parent_comment, self.comment)
        self.assertEqual(notif_to_author.recipient, self.author_comment)
        self.assertEqual(notif_count, 1)

    def test_no_notif_own_reply_to_yourself(self):
        """if user reply's own comment -> no notifications"""
        self.client.force_login(self.author_comment)
        url = reverse(
            "comments:process_comm",
            kwargs={"post_uuid": self.post.uuid},
        )
        data = {
            "body": "Sally reply's to herself",
            "comm_parent_id": self.comment.id,
            "post": self.post,
        }
        headers = {"HTTP_HX-Request": "true"}

        resp = self.client.post(url, data=data, **headers)

        notif_count = Notification.objects.count()

        self.assertEqual(resp.status_code, 204)
        self.assertEqual(notif_count, 0)


@override_settings(LANGUAGE_CODE="en", LANGUAGES=(("en", "English"),))
class NotificationCheck(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.author_root_comment = UserFactory(username="sally")
        self.replier1 = UserFactory(username="sam")
        self.replier2 = UserFactory(username="sam")
        self.replier3 = UserFactory(username="sam")

        self.root_comment = CommentFactory(user=self.author_root_comment)
        self.root_comment.add_child(
            user=self.replier1,
            post=self.root_comment.post,
            reply_to=self.author_root_comment,
        )
        self.root_comment.add_child(
            user=self.replier2,
            post=self.root_comment.post,
            reply_to=self.author_root_comment,
        )
        self.root_comment.add_child(
            user=self.replier3,
            post=self.root_comment.post,
            reply_to=self.author_root_comment,
        )
        # another post
        self.post = PostFactory.create(
            title_en="Sky",
            content_en="dial",
            status=2,
        )
        self.root_comment2 = CommentFactory(
            user=self.author_root_comment, post=self.post
        )
        self.root_comment2.add_child(
            user=self.replier1,
            post=self.root_comment2.post,
            reply_to=self.author_root_comment,
        )
        self.root_comment2.add_child(
            user=self.replier2,
            post=self.root_comment2.post,
            reply_to=self.author_root_comment,
        )

    def test_count_all_notifications(self):
        """count all notifications for a given user"""
        self.client.force_login(self.author_root_comment)
        url = reverse(
            "notifications:show_notifs",
        )
        resp = self.client.get(url)

        notifs = Notification.objects.all_unread_notifics(self.author_root_comment)

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(notifs.count(), 5)
        self.assertFalse(notifs[0].read)

    def test_mark_notific_as_read(self):
        """mark all notifications as read"""
        self.client.force_login(self.author_root_comment)
        url = reverse(
            "notifications:mark_read",
        )
        headers = {"HTTP_HX-Request": "true", "HTTP_REFERER": "foo"}

        resp = self.client.post(url, **headers)

        notifs = Notification.objects.all()

        self.assertEqual(resp.status_code, 200)
        self.assertTrue(notifs[0].read)
        self.assertTrue(notifs[1].read)

    def test_partial_mark_notific_as_read(self):
        """
        htmx via menu: mark notifs as read only for post thread (root) comment;

        """
        start_unread_count = Notification.objects.count_unread_notifics(
            self.author_root_comment
        )
        self.client.force_login(self.author_root_comment)
        url = reverse(
            "posts:get_branch",
            kwargs={"slug": self.post.slug, "thread_uuid": self.root_comment2.uuid},
        )
        headers = {"HTTP_HX-Request": "true", "HTTP_REFERER": "foo"}

        resp = self.client.get(url, **headers)

        end_unread_count = Notification.objects.count_unread_notifics(
            self.author_root_comment
        )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(start_unread_count, 5)
        self.assertEqual(end_unread_count, 3)

    def test_failure_notific_as_read(self):
        """fail to mark all notifications as read"""
        self.client.force_login(self.author_root_comment)
        url = reverse(
            "notifications:mark_read",
        )

        with self.assertRaises(HtmxFailureError) as e:
            resp = self.client.post(url)  # noqa

        self.assertEqual(str(e.exception), _("Something went wrong.Please try later"))
