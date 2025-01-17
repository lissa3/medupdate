import factory
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from faker import Faker

User = get_user_model()

faker = Faker()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ("username", "email")

    username = factory.Sequence(lambda n: f"user-{n}")
    email = factory.LazyAttribute(lambda _: faker.unique.email())
    password = factory.PostGenerationMethodCall("set_password", "12345abc")


class AdminSupUserFactory(UserFactory):
    is_staff = True
    is_superuser = True


class StaffUserFactory(UserFactory):
    is_staff = True
    is_superuser = False
