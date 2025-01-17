# from contextlib import contextmanager
from unittest.mock import Mock

from django.contrib.auth import get_user_model
from django.db.models.signals import post_delete, post_save
from django.test import TestCase

from src.accounts.tests.factories import UserFactory
from src.profiles.models import Profile
from src.profiles.tests.factories.profile_factory import ProfileFactory

User = get_user_model()


class UserTestCase(TestCase):
    def setUp(self) -> None:
        pass

    def test_user_signal(self):
        """test forming profile via signal when new user created"""
        handler = Mock()
        post_save.connect(handler, sender=User)
        user = UserFactory()
        self.assertTrue(handler.called)
        self.assertIsNotNone(user.profile.id)

    def test_profile_signal(self):
        """delete profile signal"""
        handler = Mock()
        post_delete.connect(handler, sender=Profile)
        profile = ProfileFactory()
        user = profile.user
        profile.delete()

        self.assertTrue(handler.called)
        self.assertFalse(user.is_active)
