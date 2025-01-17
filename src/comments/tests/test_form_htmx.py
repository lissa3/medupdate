from django.test import override_settings
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django_webtest import WebTest

from src.accounts.tests.factories import UserFactory
from src.comments.models import Comment
from src.posts.tests.factories import PostFactory


@override_settings(LANGUAGE_CODE="en", LANGUAGES=(("en", "English"),))
class HtmxRenderedCommentsTest(WebTest):
    def setUp(self) -> None:
        super().setUp()
        author_comment = UserFactory(username="sally")
        self.post = PostFactory.create(
            title_en="Bell's palsy",
            content_en="herpes virus, treatment,prednisone",
            status=2,
        )
        self.comment = Comment.add_root(
            post=self.post, user=author_comment, body="it's me root comment"
        )

        self.url = reverse("posts:post_detail", kwargs={"slug": self.post.slug})

    def test_root_comment_on_post_detail(self):
        all_comms_url = reverse(
            "comments:all_comms", kwargs={"post_uuid": self.post.uuid}
        )
        headers = {"HTTP_HX-Request": "true"}
        response = self.client.get(all_comms_url, **headers)

        comments = response.context["comments"]

        self.assertEqual(len(comments), 1)
        self.assertTemplateUsed(response, "components/comms/wraps.html")
