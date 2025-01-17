from datetime import date

from django.template import Context, Template
from django.test import TestCase, override_settings
from faker import Faker
from freezegun import freeze_time
from taggit.models import Tag

from src.posts.models.categ_model import Category
from src.posts.models.post_model import Post
from src.posts.tests.factories import PostFactory

fake = Faker()


class CategsTempTagsTest(TestCase):
    """test custom inclusion tag for rendering nested categories"""

    TEMPLATE = Template("{% load tree_collections %} {% show_categs %}")

    def setUp(self):
        self.categ_root_1 = Category.add_root(name="apple")
        self.categ_root_2 = self.categ_root_1.add_sibling(name="sun")
        self.categ_kid_2 = self.categ_root_2.add_child(name="flower")

    def test_categs_shows(self):
        rendered = self.TEMPLATE.render(Context({}))
        self.assertIn(self.categ_root_1.name, rendered)
        self.assertIn(self.categ_root_2.name, rendered)
        self.assertIn(self.categ_kid_2.name, rendered)


@override_settings(LANGUAGE_CODE="ru", LANGUAGES=(("ru", "Russian"),))
class TagsInTempTest(TestCase):
    """test custom inclusion tag for rendering tags"""

    TEMPLATE = Template("{% load tree_collections %} {% show_tags %}")

    def setUp(self):
        self.tag1 = Tag.objects.create(name="слон")
        self.tag2 = Tag.objects.create(name="глаз")
        self.tag3 = Tag.objects.create(name="дерево")
        self.post_1 = PostFactory(
            status=Post.CurrentStatus.PUB.value, tags=(self.tag1, self.tag2)
        )

    def test_tags_shows_published_post(self):
        """if post with tags public -> template with tags"""
        rendered = self.TEMPLATE.render(Context({}))
        self.assertIn(self.tag1.name, rendered)
        self.assertIn(self.tag2.name, rendered)

    def test_no_tag_not_published(self):
        """if post with tags NOT public -> no tags via templ tags"""
        rendered = self.TEMPLATE.render(Context({}))
        self.assertNotIn(self.tag3.name, rendered)


@override_settings(LANGUAGE_CODE="en", LANGUAGES=(("en", "English"),))
class ArchiveTempTest(TestCase):
    TEMPLATE = Template("{% load calend %} {% show_archive %}")

    @freeze_time("2022-01-12")
    def setUp(self):
        """render only public posts(published_at via model save if status ==2)"""
        self.post_1 = PostFactory(
            status=Post.CurrentStatus.PUB.value, published_at=date(2022, 1, 12)
        )
        self.post_2 = PostFactory(
            status=Post.CurrentStatus.PUB.value, published_at=date(2022, 1, 14)
        )

    @freeze_time("2023-05-23")
    def test_archive_show(self):
        PostFactory(status=Post.CurrentStatus.PUB.value, published_at=date(2023, 5, 24))
        rendered = self.TEMPLATE.render(Context({}))

        self.assertIn(str(2022), rendered)
        self.assertIn(str(2023), rendered)
        self.assertIn("January", rendered)
        self.assertIn("May", rendered)
