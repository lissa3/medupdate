import factory

from src.contacts.models import NewsLetter


class NewsLetterFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = NewsLetter

    title = factory.Faker("word")
    text = factory.Faker("sentence")
