import factory

from src.accounts.tests.factories import UserFactory
from src.comments.models import Comment
from src.posts.tests.factories import PostFactory


class CommentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Comment

    body = factory.Faker("sentence")
    post = factory.SubFactory(PostFactory)
    user = factory.SubFactory(UserFactory)

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """
        override default manager;
        create root comment without children;
        """
        return Comment.add_root(**kwargs)
