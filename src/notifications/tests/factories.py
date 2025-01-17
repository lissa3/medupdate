import factory

from src.accounts.models import User
from src.comments.models import Comment
from src.notifications.models import Notification
from src.posts.models.post_model import Post


class NotificationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Notification

    recipient = factory.SubFactory(User)
    text = factory.Faker("sentence")
    post = factory.SubFactory(Post)
    comment = factory.SubFactory(Comment)
