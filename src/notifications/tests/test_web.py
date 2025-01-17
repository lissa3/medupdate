from datetime import date

from django.contrib.auth import get_user_model
from django.db.models import signals
from django.test import override_settings
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django_webtest import WebTest
from factory.django import mute_signals
from freezegun import freeze_time

from src.accounts.tests.factories import UserFactory
from src.comments.tests.factories import CommentFactory

User = get_user_model()


@override_settings(LANGUAGE_CODE="en", LANGUAGES=(("en", "English"),))
class NotificationsCommentsTestCase(WebTest):
    def setUp(self) -> None:
        super().setUp()
        self.author_root_comment = UserFactory(username="sally")
        self.replier1 = UserFactory(username="sam")
        self.replier2 = UserFactory(username="sam")
        self.replier3 = UserFactory(username="sam")

        self.root_comment = CommentFactory(user=self.author_root_comment)
        self.root_comment.add_child(
            user=self.replier1,
            post=self.root_comment.post,
            reply_to=self.author_root_comment,
        )
        self.root_comment.add_child(
            user=self.replier2,
            post=self.root_comment.post,
            reply_to=self.author_root_comment,
        )
        self.root_comment.add_child(
            user=self.replier3,
            post=self.root_comment.post,
            reply_to=self.author_root_comment,
        )
        self.app.set_user(self.author_root_comment)
        self.url = reverse("home")
        self.resp = self.app.get(self.url)

    def test_change_count_unread_notifs(self):
        """top menu UI: with logged-in user and his notifs"""
        menu_links = self.resp.html.findAll("a", class_="dropdown-toggle")

        assert self.resp.status_code == 200
        assert "sally" in menu_links[0].text
        assert "3" in menu_links[1].text

    def test_top_menu_presence_link_to_htmx(self):
        """menu dropdown  has <a> tag with href to trigger htmx req"""
        dropdow_notifications = self.resp.html.find("div", id="notis")
        a_link = self.resp.html.find_all("a", class_="dropdown-toggle")[1]
        href = a_link.attrs["hx-get"]

        assert self.resp.status_code == 200
        assert href is not None
        assert dropdow_notifications is not None


@freeze_time("2023-01-01")
@override_settings(LANGUAGE_CODE="en", LANGUAGES=(("en", "English"),))
class NotificationsAdminTestCase(WebTest):
    def setUp(self) -> None:
        super().setUp()
        self.user_to_ban = UserFactory(username="boze anna")
        self.app.set_user(self.user_to_ban)
        self.url = reverse("home")

    def test_change_count_unread_notifs(self):
        """top menu UI: admin msg for banned user"""

        start_ban = date(2023, 1, 1)
        end_ban = date(2023, 1, 15)

        with mute_signals(signals.post_save):
            self.user_to_ban.banned = True
            self.user_to_ban.save()
            self.user_to_ban.refresh_from_db()

        resp = self.app.get(self.url)

        dropdow_notifications = resp.html.find("div", id="notis")
        menu_links = resp.html.findAll("a", class_="dropdown-toggle")
        print("--------------------")
        print(menu_links)
        print("=================")
        print(menu_links[1].text)

        assert resp.status_code == 200
        assert "1" in menu_links[1].text
        assert dropdow_notifications is not None
        assert self.user_to_ban.profile.start_ban == start_ban
        assert self.user_to_ban.profile.end_ban == end_ban
