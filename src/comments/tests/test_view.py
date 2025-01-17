from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from src.accounts.tests.factories import UserFactory
from src.comments.models import Comment
from src.posts.tests.factories import PostFactory

User = get_user_model()


@override_settings(LANGUAGE_CODE="en", LANGUAGES=(("en", "English"),))
class HtmxCommentsFunctionsViewsTestCase(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.user = UserFactory(username="tata")
        self.anna_author = UserFactory(username="anna")
        self.author_comment = UserFactory(username="sally")
        self.post = PostFactory.create(
            title_en="Bell's palsy",
            content_en="herpes virus, treatment,prednisone",
            status=2,
        )
        self.comment = Comment.add_root(
            post=self.post, user=self.author_comment, body="it's me root comment"
        )
        self.anna_comment = Comment.add_root(
            post=self.post, user=self.anna_author, body="I will be soon banned"
        )

    def test_get_reply_form(self):
        """logged-in and not banned user gets reply form on post detail"""
        user = UserFactory()
        self.client.force_login(user)

        url = reverse(
            "comments:add_comm",
            kwargs={"post_uuid": self.post.uuid, "comm_id": self.comment.id},
        )
        headers = {"HTTP_HX-Request": "true"}
        resp = self.client.get(url, **headers)
        form = resp.context["form"]

        self.assertEqual(resp.status_code, 200)
        self.assertFalse(form.is_bound)
        self.assertTrue(form.initial, {"comm_parent_id": str(self.comment.id)})

    def test_failure_get_reply_form(self):
        """if NOT htmx _> auth and not banned user gets No reply form on post detail"""
        user = UserFactory()
        self.client.force_login(user)
        url = reverse(
            "comments:add_comm",
            kwargs={"post_uuid": self.post.uuid, "comm_id": self.comment.id},
        )

        resp = self.client.get(url)

        self.assertEqual(resp.status_code, 400)

    def test_failure_process_reply_form(self):
        """if no htmx -> bad request"""
        self.client.force_login(self.anna_author)
        url = reverse(
            "comments:add_comm",
            kwargs={"post_uuid": self.post.uuid, "comm_id": self.comment.id},
        )

        resp = self.client.get(url)

        self.assertEqual(resp.status_code, 400)

    def test_no_reply_form_for_banned(self):
        """auth but banned user gets no reply form"""
        self.anna_author.banned = True
        self.anna_author.save()
        self.client.force_login(self.anna_author)
        url = reverse(
            "comments:add_comm",
            kwargs={"post_uuid": self.post.uuid, "comm_id": self.comment.id},
        )
        headers = {"HTTP_HX-Request": "true"}

        resp = self.client.get(url, **headers)

        self.assertEqual(resp.status_code, 403)

    def test_post_reply_comment(self):
        """
        logged and not banned user can add child
        comment(reply to a root comment)
        """
        start_comments = Comment.objects.all()
        count_start = start_comments.count()
        user = UserFactory()
        self.client.force_login(user)
        url = reverse("comments:process_comm", kwargs={"post_uuid": self.post.uuid})
        data = {"body": "reply to a root comment", "comm_parent_id": self.comment.id}
        headers = {"HTTP_HX-Request": "true"}
        resp = self.client.post(url, data=data, **headers)

        self.comment.refresh_from_db()

        final_comments = Comment.objects.all()
        parent = final_comments.first()

        kids = parent.get_children_count()
        kid = parent.get_children()[0]

        self.assertEqual(resp.status_code, 204)
        self.assertEqual(count_start, 2)
        self.assertEqual(final_comments.count(), 3)
        self.assertEqual(kids, 1)
        self.assertEqual(kid.reply_to, self.author_comment)

    def test_no_reply_comment_for_banned(self):
        """
        logged-in but banned user can not add
        child comment(reply to a root comment)
        """
        self.anna_author.banned = True
        self.anna_author.save()
        self.client.force_login(self.anna_author)
        url = reverse(
            "comments:process_comm",
            kwargs={"post_uuid": self.post.uuid},
        )
        data = {
            "body": "reply to a root comment",
            "comm_parent_id": self.anna_comment.id,
        }
        headers = {"HTTP_HX-Request": "true"}

        resp = self.client.post(url, data=data, **headers)

        self.assertEqual(resp.status_code, 403)

    def test_auth_comment_tools(self):
        """
        auth and not banned comment author has links to
        fetch a form for edit and delete"""

        self.client.force_login(self.author_comment)
        url = reverse("comments:all_comms", kwargs={"post_uuid": self.post.uuid})
        headers = {"HTTP_HX-Request": "true"}
        resp = self.client.get(url, **headers)

        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'hx-target="#dialog"')
        self.assertContains(resp, 'hx-get="/en/comments/edit-comm')
        self.assertContains(resp, 'hx-get="/en/comments/process-delete')

    def test_banned_author_comment_no_tools(self):
        """banned comment author gets NO links to fetch a form for edit and delete"""
        self.anna_author.banned = True
        self.anna_author.save()
        self.client.force_login(self.anna_author)
        url = reverse("comments:all_comms", kwargs={"post_uuid": self.post.uuid})
        headers = {"HTTP_HX-Request": "true"}
        resp = self.client.get(url, **headers)

        self.assertEqual(resp.status_code, 200)

        self.assertNotContains(resp, 'hx-target="#dialog"')
        self.assertNotContains(resp, 'hx-get="/en/comments/edit-comm')
        self.assertNotContains(resp, 'hx-get="/en/comments/process-delete')

    def test_not_author_auth_user_no_comment_tools(self):
        """auth user but NOT comment author has No links for edit and delete"""

        self.client.force_login(self.user)
        url = reverse("comments:all_comms", kwargs={"post_uuid": self.post.uuid})
        headers = {"HTTP_HX-Request": "true"}
        resp = self.client.get(url, **headers)

        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'hx-target="#dialog"')
        self.assertNotContains(resp, 'hx-get="/en/comments/edit-comm')
        self.assertNotContains(resp, 'hx-get="/en/comments/process-delete')

    def test_anonymous_no_reply_no_comment_tools(self):
        """un-auth user has no link to reply or edit/delete cooment"""

        url = reverse("comments:all_comms", kwargs={"post_uuid": self.post.uuid})
        headers = {"HTTP_HX-Request": "true"}
        resp = self.client.get(url, **headers)

        self.assertEqual(resp.status_code, 200)
        self.assertNotContains(resp, 'hx-target="#dialog"')
        self.assertNotContains(resp, 'hx-get="/en/comments/edit-comm')
        self.assertNotContains(resp, 'hx-get="/en/comments/process-delete')
