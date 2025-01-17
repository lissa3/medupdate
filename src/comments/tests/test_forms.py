from django.test import override_settings
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django_webtest import WebTest

from src.accounts.tests.factories import UserFactory
from src.comments.models import Comment
from src.posts.tests.factories import PostFactory


@override_settings(LANGUAGE_CODE="en", LANGUAGES=(("en", "English"),))
class CommentPostAuthDetailWebTest(WebTest):
    def setUp(self) -> None:
        super().setUp()
        self.user = UserFactory()

        self.post = PostFactory.create(
            title_en="Bell's palsy",
            content_en="herpes virus, treatment,prednisone",
            status=2,
        )
        self.url = reverse("posts:post_detail", kwargs={"slug": self.post.slug})

    def test_auth_user_comment_form_post_detail_page(self):
        """auth user has top comment form"""
        self.app.set_user(self.user)  # user is auth-ed

        resp = self.app.get(self.url)

        comm_form = resp.forms["top_form"]

        self.assertEqual(resp.status_code, 200)
        self.assertIsNotNone(comm_form)

    def test_un_auth_comment_form_post_detail_page(self):
        """NOT auth user has NO top comment form"""

        resp = self.app.get(self.url)

        comm_form = resp.html.find("form", id="top_form")

        self.assertEqual(resp.status_code, 200)
        self.assertIsNone(comm_form)


@override_settings(LANGUAGE_CODE="en", LANGUAGES=(("en", "English"),))
class TopCommentsPostDetailWebTestCase(WebTest):
    def setUp(self) -> None:
        super().setUp()
        self.user = UserFactory()

        self.post = PostFactory.create(
            title_en="Bell's palsy",
            content_en="herpes virus, treatment,prednisone",
            status=2,
        )
        self.url = reverse("posts:post_detail", kwargs={"slug": self.post.slug})
        self.app.set_user(self.user)
        self.resp = self.app.get(self.url)

    def test_submit_root_commet_on_post_detail_page(self):
        """use unbound form from setup to create a root comment
        without kids or parents; created comment on UI"""
        comments = Comment.objects.all()
        start_count = comments.count()
        comm_form = self.resp.forms["top_form"]
        comm_form["body"] = "Root comment added"

        resp_submit = comm_form.submit().follow()

        end_count = Comment.objects.all().count()

        root_comment = Comment.objects.last()

        is_root = root_comment.get_parent()

        children_count = root_comment.get_children_count()

        div_comms = resp_submit.html.find("div", class_="comms")

        self.assertEqual(self.resp.status_code, 200)
        self.assertEqual(resp_submit.status_code, 200)
        self.assertIsNotNone(comm_form)
        self.assertEqual(start_count, 0)
        self.assertEqual(end_count, 1)
        self.assertIsNone(is_root)
        self.assertEqual(children_count, 0)
        self.assertIsNotNone(div_comms)

    def test_error_submit_no_body_root_commet(self):
        """form error test: root comment is empty"""

        comm_form = self.resp.forms["top_form"]
        comm_form["body"] = ""

        resp_submit = comm_form.submit()

        comments_count = Comment.objects.all().count()

        div_comms = resp_submit.html.find("div", class_="comms")

        msg_txt = _("This field is required.")

        self.assertEqual(self.resp.status_code, 200)
        self.assertEqual(resp_submit.status_code, 200)
        self.assertIsNotNone(comm_form)
        self.assertEqual(comments_count, 0)
        self.assertIsNone(div_comms)
        self.assertEqual(
            resp_submit.context["form"].errors,
            {"body": [msg_txt]},
        )
