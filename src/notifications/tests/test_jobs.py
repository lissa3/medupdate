from django.core.management import call_command
from django.test import TestCase, override_settings
from freezegun import freeze_time

from src.accounts.tests.factories import UserFactory
from src.notifications.management.commands import unban  # noga


@override_settings(LANGUAGE_CODE="ru", LANGUAGES=(("ru", "Russian"),))
class TestUnbanUsersJob(TestCase):
    @freeze_time("2023-01-01")
    def setUp(self) -> None:
        super().setUp()
        self.user = UserFactory()
        self.user.banned = True
        self.user.save()
        self.user.refresh_from_db()

    @freeze_time("2023-01-16")
    def test_unban_user(self):
        """
        if current date > end_ban date unban user
        (via cron on remote)
        """
        call_command("unban")
        self.user.refresh_from_db()

        self.assertFalse(self.user.banned)
        self.assertIsNone(self.user.profile.end_ban)
        self.assertIsNone(self.user.profile.start_ban)
