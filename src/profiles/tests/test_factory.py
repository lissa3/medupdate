import time_machine
from django.test import TestCase

from src.accounts.tests.factories import UserFactory
from src.profiles.models import Profile

from .factories.profile_factory import ProfileFactory


class ProfileTestCase(TestCase):
    @time_machine.travel("2023-01-01")
    def setUp(self) -> None:
        self.user = UserFactory(username="tata")
        # self.client.login(email=self.user.email, password="secret")

    def test_profile_attributes(self):
        """test forming profile when new user created"""
        profile = Profile.objects.get(user=self.user)

        self.assertEqual(profile.user.banned, False)
        self.assertEqual(profile.user.username, "tata")
        self.assertEqual(profile.admin_info, "")
        self.assertEqual(profile.avatar, "")
        self.assertFalse(profile.user.blackListEmail, False)
        self.assertTrue(profile.created_at, "2023-01-01")
        self.assertEqual(profile.want_news, False)

    def test_want_news(self):
        """profile user wants news"""
        profile_news = ProfileFactory(want_news=True)
        self.assertEqual(profile_news.want_news, True)
