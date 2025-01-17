from datetime import timezone

import factory
import factory.fuzzy
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from factory.django import DjangoModelFactory
from faker import Faker
from taggit.models import Tag

from src.accounts.tests.factories import StaffUserFactory, UserFactory
from src.posts.models.categ_model import Category
from src.posts.models.media_model import Video
from src.posts.models.post_model import Post
from src.posts.models.relation_model import Relation

fake = Faker()


class CategoryFactory(DjangoModelFactory):
    name = factory.Faker("word")
    icon = factory.django.ImageField()

    class Meta:
        model = Category

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """
        override default manager;
        create root categ without children;
        """
        return Category.add_root(**kwargs)


class PostFactory(DjangoModelFactory):
    """published_at is not longer auto created"""

    author = factory.SubFactory(StaffUserFactory)
    # published_at = fake.date_time(tzinfo=timezone.utc)
    status = factory.fuzzy.FuzzyChoice(Post.CurrentStatus.values)
    title_ru = _("море")
    content_ru = _("земля")
    title_en = _("see")
    content_en = _("earth")

    class Meta:
        model = "posts.Post"

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            self.tags.add(*extracted)


class TagFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda n: f"tag {n}")
    slug = factory.LazyAttribute(lambda m: slugify(m.name))

    class Meta:
        model = Tag

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """create a  tag"""
        return Tag.objects.get_or_create({"name": elem} for elem in ["apple", "pier"])


class RelationFactory(factory.django.DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    post = factory.SubFactory(PostFactory)

    class Meta:
        model = Relation


class VideoFactory(DjangoModelFactory):
    url = "https://youtu.be/74_TNsHWBxY?si=68IgV9bkBL40Dgmh&t=29"  # fake.image_url()

    class Meta:
        model = Video
