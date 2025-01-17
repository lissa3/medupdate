import factory
from django.db.models.signals import post_save

from src.accounts.tests.factories import UserFactory
from src.profiles.models import Profile


@factory.django.mute_signals(post_save)
class ProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Profile
        django_get_or_create = ("user",)

    user = factory.SubFactory(UserFactory)
    avatar = factory.django.ImageField()
