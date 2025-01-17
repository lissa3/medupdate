from django.test import Client, TestCase, override_settings
from django.urls import reverse

from src.accounts.tests.factories import StaffUserFactory, UserFactory
from src.comments.tests.factories import CommentFactory
from src.posts.models.categ_model import Category
from src.posts.models.post_model import Post
from src.posts.models.relation_model import Relation
from src.posts.tests.factories import PostFactory, RelationFactory


class PostCategsTestCase(TestCase):
    def setUp(self) -> None:
        self.categ_root_1 = Category.add_root(name="parent1")
        self.categ_root_2 = self.categ_root_1.add_sibling(name="parent2")
        self.categ_kid1 = self.categ_root_2.add_child(name="kid1_parent2")
        self.categ_kid2 = self.categ_root_2.add_child(name="kid2_parent2")

        self.post_1 = PostFactory(
            status=Post.CurrentStatus.PUB.value, categ=self.categ_root_1
        )
        self.post_2 = PostFactory(
            status=Post.CurrentStatus.PUB.value, categ=self.categ_kid1
        )
        self.post_3 = PostFactory(
            status=Post.CurrentStatus.PUB.value, categ=self.categ_kid2
        )
        self.post_4 = PostFactory(
            categ=self.categ_kid2, status=Post.CurrentStatus.DRAFT.value
        )
        self.post_5 = PostFactory()  # default categ = unspecified
        self.post_6 = PostFactory(
            categ=self.categ_root_2, status=Post.CurrentStatus.PUB.value
        )
        self.client = Client()

    @override_settings(LANGUAGE_CODE="en", LANGUAGES=(("en", "English"),))
    def test_posts_categ_with_kids(self):
        """display public posts related to a given categ and it's decendants)"""
        path = reverse("posts:cat_search", kwargs={"slug": self.categ_root_2.slug})
        headers = {"HTTP_HX-Request": "true"}

        response = self.client.get(path, **headers)

        posts = response.context["posts"]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(posts), 3)

    @override_settings(LANGUAGE_CODE="en", LANGUAGES=(("en", "English"),))
    def test_posts_categ_no_kids(self):
        """display public posts related to a given categ
        without decendants)"""
        categs_count = Category.objects.count()
        path = reverse("posts:cat_search", kwargs={"slug": self.categ_root_1.slug})

        response = self.client.get(path)

        posts = response.context["posts"]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(posts), 1)
        self.assertEqual(categs_count, 5)


class PostListTestCase(TestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        self.staff = StaffUserFactory()
        self.posts_public = PostFactory.create_batch(
            10, status=Post.CurrentStatus.PUB.value
        )
        self.posts_drafts = PostFactory.create_batch(
            2, status=Post.CurrentStatus.DRAFT.value
        )
        self.client = Client()

    @override_settings(LANGUAGE_CODE="ru", LANGUAGES=(("ru", "Russian"),))
    def test_view_public_posts_ru(self):
        """show only public posts; lang ru in url path"""
        path = reverse("posts:post_list")
        lang = path.split("/")[1]
        response = self.client.get(path)

        posts_count = Post.objects.get_public().count()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(posts_count, 10)
        self.assertEqual("ru", lang)
        self.assertEqual(
            response.context_data["paginator"].count, Post.objects.get_public().count()
        )

    @override_settings(LANGUAGE_CODE="en", LANGUAGES=(("en", "English"),))
    def test_public_posts_en(self):
        """show only public posts; lang en in url path"""
        path = reverse("posts:post_list")
        lang = path.split("/")[1]
        response = self.client.get(path)
        posts_count = Post.objects.get_public().count()

        self.assertEqual(response.status_code, 200)
        self.assertEqual("en", lang)
        self.assertEqual(posts_count, 10)
        self.assertEqual(
            response.context_data["paginator"].count, Post.objects.get_public().count()
        )


class PostSearchLangTestCase(TestCase):
    def setUp(self) -> None:
        super().setUp()

        self.post_1 = PostFactory.create(
            title_ru="Паралич Бэлла",
            content_ru="вирус герпеса, лечение преднизолоном,инфекциями",
            title_en="Bell's palsy",
            content_en="herpes virus, treatment,prednisone,infections",
            status=2,
        )

        self.post_2 = PostFactory(
            title_ru="Инфекция кожи",
            title_en="Skin infections",
            content_ru="Лечение чего-то там",
            content_en="Treatment",
            status=2,
        )
        self.post_3 = PostFactory(
            status=2,
            title_ru="Гипербиллирубинемия у новорождённых",
            content_ru="Фото терапия ",
            title_en="Newborns Hyperbilirubinemia",
            content_en="Photo therapy",
        )
        self.post_4 = PostFactory(
            status=0,
            title_ru="Гипербиллирубинемия у новорождённых",
            content_ru="Фото терапия ",
            title_en="Newborns Hyperbilirubinemia",
            content_en="Photo therapy",
        )
        self.post_5 = PostFactory(
            status=1,
            title_ru="Гипербиллирубинемия у новорождённых",
            content_ru="Фото терапия ",
            title_en="Newborns Hyperbilirubinemia",
            content_en="Photo therapy",
        )

    @override_settings(LANGUAGE_CODE="ru", LANGUAGES=(("ru", "Russian"),))
    def test_ru(self):
        """search in russian lang content"""
        url = reverse("posts:search_posts")

        search_word = "инфекция"
        data = {"q": search_word, "lang": "ru", "honeypot": ""}
        resp = self.client.get(url, data)

        posts = resp.context_data["posts"]
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(posts), 2)

    @override_settings(LANGUAGE_CODE="ru", LANGUAGES=(("ru", "Russian"),))
    def test_not_public_ru(self):
        """results for posts only with status public"""
        url = reverse("posts:search_posts")

        search_word = "Гипербиллирубинемия"
        data = {"q": search_word, "lang": "ru", "honeypot": ""}
        resp = self.client.get(url, data)

        posts = resp.context_data["posts"]
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(posts), 1)

    @override_settings(LANGUAGE_CODE="ru", LANGUAGES=(("ru", "Russian"),))
    def test_no_results_ru(self):
        """no search results in russian"""
        url = reverse("posts:search_posts")
        search_word = "квартирус"
        data = {"q": search_word, "lang": "ru", "honeypot": ""}
        resp = self.client.get(url, data)

        posts = resp.context_data["posts"]

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(posts), 0)

    @override_settings(LANGUAGE_CODE="en", LANGUAGES=(("en", "English"),))
    def test_in_en(self):
        """search in english lang content"""
        url = reverse("posts:search_posts")
        search_word = "Hyperbilirubinemia"
        data = {"q": search_word, "lang": "en", "honeypot": ""}
        resp = self.client.get(url, data)

        posts = resp.context_data["posts"]
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(posts), 1)

    @override_settings(LANGUAGE_CODE="en", LANGUAGES=(("en", "English"),))
    def test_no_results_en(self):
        """no results in english"""
        url = reverse("posts:search_posts")
        search_word = "kite"
        data = {"q": search_word, "lang": "en", "honeypot": ""}
        resp = self.client.get(url, data)

        posts = resp.context_data["posts"]
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(posts), 0)


@override_settings(LANGUAGE_CODE="en", LANGUAGES=(("en", "English"),))
class PostDetailAndCommentsTestCase(TestCase):
    def setUp(self) -> None:
        self.post_1 = PostFactory(status=Post.CurrentStatus.PUB.value)
        self.post_2 = PostFactory(status=Post.CurrentStatus.PUB.value)
        self.post_3 = PostFactory(status=Post.CurrentStatus.DRAFT.value)
        self.user = UserFactory(username="tissa")
        self.comment_1 = CommentFactory(body="foo", post=self.post_1, user=self.user)
        self.comment_2 = CommentFactory(
            body="tired cat", post=self.post_1, user=self.user
        )
        self.comment_3 = CommentFactory(body="no fun", post=self.post_2, user=self.user)

    def test_fail_to_get_draft_posts(self):
        """no detail view for not public post"""
        path = reverse("posts:post_detail", kwargs={"slug": self.post_3.slug})

        resp = self.client.get(path)

        self.assertEqual(resp.status_code, 404)

    def test_success_get_public_post(self):
        """detail view for public post"""
        path = reverse("posts:post_detail", kwargs={"slug": self.post_1.slug})

        resp = self.client.get(path)

        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.context_data["post"])

    def test_count_posts_comments(self):
        """comments for a given post;"""
        path = reverse("posts:post_detail", kwargs={"slug": self.post_1.slug})

        response = self.client.get(path)

        count_comments = response.context["comms_total"]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(count_comments, 2)


class UserLikedTestCase(TestCase):
    def setUp(self) -> None:
        self.post = PostFactory(status=Post.CurrentStatus.PUB.value)
        self.user = UserFactory(username="tissa")

    @override_settings(LANGUAGE_CODE="en", LANGUAGES=(("en", "English"),))
    def test_can_like(self):
        """htmx req; auth use can like post"""
        self.client.force_login(self.user)
        headers = {"HTTP_HX-Request": "true"}

        path = reverse("posts:track_likes")
        post_start_like = self.post.count_likes
        data = {"post_uuid": self.post.uuid, "user_id": self.user.id}

        resp = self.client.post(path, data=data, **headers)

        self.post.refresh_from_db()
        post_new_like = self.post.count_likes
        total_likes = resp.context["total_likes"]

        self.assertNotEqual(post_start_like, post_new_like)
        self.assertEqual(total_likes, 1)

        # ------second click (again) == remove prev like --------
        data = {"post_uuid": self.post.uuid, "user_id": self.user.id}

        resp = self.client.post(path, data=data, **headers)

        self.post.refresh_from_db()
        post_new_like_second = self.post.count_likes
        total_likes_second = resp.context["total_likes"]

        self.assertEqual(total_likes_second, post_new_like_second)


@override_settings(LANGUAGE_CODE="en", LANGUAGES=(("en", "English"),))
class UserBookmarkTestCase(TestCase):
    def setUp(self) -> None:
        author = StaffUserFactory(username="great_author")
        self.post = PostFactory(status=Post.CurrentStatus.PUB.value)
        self.post2 = PostFactory(status=Post.CurrentStatus.PUB.value, author=author)
        self.user = UserFactory(username="zoo")

    def test_can_bookmark(self):
        """auth use can add post to bookmark"""
        self.client.force_login(self.user)
        path = reverse("posts:change_bookmark", kwargs={"action": "add"})
        data = {"post_uuid": self.post.uuid, "profile_uuid": self.user.profile.uuid}

        self.client.post(path, data=data)

        finish = Relation.objects.count()

        self.assertEqual(finish, 1)

    def test_delete_bookmark(self):
        """auth user delete from bookmark"""
        self.client.force_login(self.user)
        obj = RelationFactory(user=self.user, post=self.post, in_bookmark=True)
        start = Relation.objects.count()
        path = reverse("posts:change_bookmark", kwargs={"action": "delete"})
        data = {"post_uuid": self.post.uuid, "profile_uuid": self.user.profile.uuid}
        headers = {"HTTP_HX_Request": "true", "HTTP_REFERER": "foo"}

        self.client.post(path, data=data, **headers)
        obj.refresh_from_db()

        finish = Relation.objects.count()

        self.assertEqual(start, finish)
        self.assertFalse(obj.in_bookmark)

    def test_posts_in_bookmarks(self):
        """
        display list of posts in bookmarks selected by auth users
        """
        user = UserFactory(username="sunny")
        user_x = UserFactory(username="one")

        self.client.force_login(user)
        RelationFactory(post=self.post, user=user, in_bookmark=True)
        RelationFactory(post=self.post, user=user_x, in_bookmark=True)
        RelationFactory(post=self.post2, user=user, in_bookmark=True)

        url = reverse("posts:bmark_collection")

        resp = self.client.get(url)

        count_posts = resp.context["posts"]

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(count_posts.count(), 2)
