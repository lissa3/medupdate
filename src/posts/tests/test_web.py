from datetime import datetime
from datetime import timezone as tz
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import override_settings
from django.urls import reverse
from django_webtest import WebTest
from freezegun import freeze_time
from taggit.models import Tag
from webtest import TestApp

from src.accounts.tests.factories import AdminSupUserFactory, UserFactory
from src.contacts.models import NewsLetter
from src.contacts.tests.factories import NewsLetterFactory
from src.core.utils.admin_help import admin_change_url
from src.posts.models.post_model import Post
from src.posts.tests.factories import CategoryFactory, PostFactory, RelationFactory

User = get_user_model()
TestApp.__test__ = False


class TestAdminPostForm(WebTest):
    def setUp(self):
        super().setUp()
        self.user = AdminSupUserFactory()
        self.app.set_user(self.user)
        self.letter = NewsLetterFactory(letter_status=1)
        self.letter = NewsLetterFactory(letter_status=1)

    def test_admin_create_post(self):
        """
        initial post form has per-filled fields:
        author(current user) and letters(status to be send);
        select field has default
        [('', False, '----'), ('1', True, 'Letter #id 1'),..]
        """
        get_form_url = reverse("admin:posts_post_add")
        resp_initial = self.app.get(get_form_url)

        self.assertEqual(resp_initial.status_code, 200)

        initial_form = resp_initial.forms["post_form"]

        last_letter = NewsLetter.objects.last()
        author_value = int(initial_form["author"].value)

        letter_value = int(initial_form["letter"].value)

        letter_options = initial_form["letter"].options

        self.assertEqual(author_value, self.user.id)
        self.assertEqual(letter_value, last_letter.id)
        self.assertEqual(len(letter_options), 3)
        self.assertEqual(letter_options[0][1], False)

    def test_admin_post_list_link_to_category(self):
        """
        post list contains a link to a category obj
        ex: # /admin/posts/category/1/change/
        """

        post = PostFactory()
        categ = post.categ
        categ_link = admin_change_url(obj=categ)

        url = reverse("admin:posts_post_changelist")

        resp = self.app.get(url)

        html_link = resp.html.find("a", href=categ_link)

        self.assertTrue(categ_link, html_link)


@override_settings(LANGUAGE_CODE="ru", LANGUAGES=(("ru", "Russian"),))
class TagSearchPostsTest(WebTest):
    def setUp(self):
        super().setUp()
        self.tag = Tag.objects.create(name="слон")
        self.tag2 = Tag.objects.create(name="иожик")
        self.post_1 = PostFactory(status=Post.CurrentStatus.PUB.value, tags=(self.tag,))
        self.post_2 = PostFactory(
            status=Post.CurrentStatus.DRAFT.value, tags=(self.tag2,)
        )

    def test_tag_seacrh(self):
        """
        posts page contains a list of tag(s) triggering
        filtering public posts based on tag

        """
        start_url = reverse("posts:post_list")
        # initial request to get a list of tags
        resp = self.app.get(start_url)
        a_tag = resp.html.find("a", class_="tag-link")
        span_tag_num = resp.html.find("span", class_="circle_num")
        a_text = a_tag.text
        href_get = a_tag.attrs["hx-get"]

        self.assertEqual(resp.status_code, 200)
        self.assertIsNotNone(resp.context["tags"])
        self.assertIn("слон", a_text)
        self.assertNotIn("иожик", a_text)
        self.assertEqual(span_tag_num.string, str(1))
        self.assertIsNotNone(href_get)

        resp2 = self.app.get(href_get)
        posts = resp2.context["posts"]

        self.assertEqual(resp2.status_code, 200)
        self.assertEqual(posts.count(), 1)


@override_settings(LANGUAGE_CODE="ru", LANGUAGES=(("ru", "Russian"),))
class CategMenuTestCase(WebTest):
    def setUp(self) -> None:
        self.categ_root = CategoryFactory(name="grand_pa")
        self.categ_pa = self.categ_root.add_child(name="pa")
        self.categ_kid = self.categ_pa.add_child(name="kid")
        self.post = PostFactory(
            categ=self.categ_kid, status=Post.CurrentStatus.PUB.value
        )

    def test_post_detail_categs_menu(self):
        """display post detail page with corresp categs as links"""
        chain_ = self.post.categ.get_name_slug_chain()
        expected_chain = {
            "path_name": "grand_pa/pa/kid",
            "path_slug": "grand_pa/pa/kid",
        }

        start_url = reverse("posts:post_detail", kwargs={"slug": self.post.slug})

        resp = self.app.get(start_url)

        post_categ_menu = resp.html.find("ol", id="post_categ")
        a_links = resp.html.find_all("a", class_="post_categ__link")
        href = a_links[0].attrs["href"]
        lang = href.split("/")[1]

        self.assertEqual(self.categ_root.get_descendants().count(), 2)
        self.assertEqual(chain_, expected_chain)
        self.assertIsNotNone(post_categ_menu)
        self.assertTrue(len(a_links), 3)
        self.assertTrue(lang, "ru")

    def test_post_count_in_categs_menu(self):
        """display root categs with public posts count;
        if post not public (yet) => count is zero
        """

        post = PostFactory(status=Post.CurrentStatus.DRAFT.value)  # noqa
        start_url = reverse("posts:post_list")

        resp = self.app.get(start_url)

        list_categ_menu = resp.html.find_all("a", class_="node-link")

        first_root_categ_count = list_categ_menu[0].text
        second_root_categ_count = list_categ_menu[3].text

        assert resp.status_code == 200
        assert "1" in first_root_categ_count
        assert "0" in second_root_categ_count


@override_settings(LANGUAGE_CODE="en", LANGUAGES=(("en", "English"),))
@freeze_time("2023-01-12")
class CalendMenuTestCase(WebTest):
    @patch("django.utils.timezone.now")
    def test_public_posts_order(self, mock_timezone):
        """show public posts per month in year: aside UI menu;
        posts created in past but later get published"""
        dt = datetime(2023, 5, 21, tzinfo=tz.utc)
        mock_timezone.return_value = dt
        PostFactory.create_batch(
            6, status=Post.CurrentStatus.PUB.value, published_at=dt
        )
        path = reverse("posts:post_list")

        resp = self.app.get(path)

        calend_menu_year = resp.html.find("button", class_="archive__data")
        a_links = resp.html.find("a", class_="calend_item")

        assert resp.status_code == 200
        assert "2023" in calend_menu_year.text
        assert "May" in a_links.text


@override_settings(LANGUAGE_CODE="ru", LANGUAGES=(("ru", "Russian"),))
class UserInteraction(WebTest):
    def setUp(self):
        super().setUp()
        self.user = UserFactory(username="sunny")
        self.post = PostFactory(status=Post.CurrentStatus.PUB.value)

    def test_auth_user_page_buttons(self):
        """
        if user auth -> detail post page contains two buttons:
        `like` and `add to bookmarks`
        """
        self.app.set_user(self.user)
        url = reverse("posts:post_detail", kwargs={"slug": self.post.slug})

        resp = self.app.get(url)

        to_like_but = resp.html.find("button", id="toLike")
        to_bookmark_but = resp.html.find("button", id="toBookMark")

        assert resp.status_code == 200
        assert to_like_but is not None
        assert to_bookmark_but is not None

    def test_no_bmark_buttons(self):
        """
        logged-in user -> detail post page has no`add to bookmarks`
        button if it already in bmarks
        """

        self.app.set_user(self.user)
        url = reverse("posts:post_detail", kwargs={"slug": self.post.slug})
        RelationFactory(user=self.user, post=self.post, in_bookmark=True)

        resp = self.app.get(url)

        to_like_but = resp.html.find("button", id="toLike")
        to_bookmark_but = resp.html.find("button", id="toBookMark")

        assert resp.status_code == 200
        assert to_like_but is not None
        assert to_bookmark_but is None

    def test_not_auth_user_page_buttons(self):
        """
        post detail for un-auth user has NO buttons:
        `like` and `add to bookmarks`
        """
        url = reverse("posts:post_detail", kwargs={"slug": self.post.slug})

        resp = self.app.get(url)

        to_like_but = resp.html.find("button", id="toLike")
        to_bookmark_but = resp.html.find("button", id="toBookMark")

        assert resp.status_code == 200
        assert to_like_but is not None
        assert to_bookmark_but is None
