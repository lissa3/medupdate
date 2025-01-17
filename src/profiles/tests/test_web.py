import os
import tempfile
from datetime import date

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import signals
from django.test import override_settings
from django.urls import reverse
from django_webtest import WebTest
from factory.django import mute_signals
from freezegun import freeze_time
from webtest import Upload

from src.accounts.tests.factories import UserFactory
from src.core.utils.base import get_temp_img_bytes
from src.profiles.models import Profile

User = get_user_model()
base_path = settings.BASE_DIR
MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(LANGUAGE_CODE="en", LANGUAGES=(("en", "English"),))
@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class MyTestCase(WebTest):
    def setUp(self):
        super().setUp()
        self.user = UserFactory.create()
        self.app.set_user(self.user)
        self.profile = Profile.objects.get(user=self.user)
        self.profile_uuid = self.profile.uuid
        self.url = reverse(
            "profiles:profile_detail", kwargs={"uuid": self.profile_uuid}
        )
        # initial request to get a form
        self.response = self.app.get(self.url)
        self.form = self.response.forms["upForm"]
        self.base_path = os.path.join(
            base_path, "src", "profiles", "tests", "files_test"
        )
        self.img_empty_file = os.path.join(self.base_path, "empty.png")
        self.err_file = (
            "Upload a valid image. The file you uploaded "
            + "was either not an image or a corrupted image."
        )
        self.err_empty_file = "The submitted file is empty."

    def test_upload_avatar_ok(self):
        """check form upload avatar diff attrs"""
        avatar = get_temp_img_bytes()
        self.form["avatar"] = Upload("zoo.jpeg", avatar, "image/jpeg")

        response = self.form.submit()

        self.assertEqual(self.form.action, self.url)
        self.assertEqual(self.form.id, "upForm")
        self.assertIsNotNone(self.form["csrfmiddlewaretoken"])
        self.assertEqual(response.status_code, 200)

    @override_settings(MAX_UPLOAD_SIZE=5)
    def test_upload_big_avatar(self):
        avatar = get_temp_img_bytes()
        self.form["avatar"] = Upload("zoo.jpeg", avatar, "image/jpeg")

        response = self.form.submit()

        err_msg = (
            f"Uploaded file should not be more than {settings.MAX_UPLOAD_SIZE} bytes"
        )

        self.assertEqual(response.json["status_code"], 404)
        self.assertEqual(response.json["err"]["avatar"][0], err_msg)

    @override_settings(MIN_UPLOAD_SIZE=1000)
    def test_upload_too_small_avatar(self):
        avatar = get_temp_img_bytes()
        self.form["avatar"] = Upload("zoo.jpeg", avatar, "image/jpeg")

        response = self.form.submit()

        err_msg = (
            f"Uploaded file should not be less than {settings.MIN_UPLOAD_SIZE} bytes."
        )

        self.assertEqual(response.json["status_code"], 404)
        self.assertEqual(response.json["err"]["avatar"][0], err_msg)

    def test_remove_avatar(self):
        """remove avatar"""
        # add avatar to profile
        self.profile.avatar = get_temp_img_bytes()
        self.form["avatar"] = None

        response_final = self.form.submit()

        self.profile.refresh_from_db()
        profile_avatar = self.profile.avatar

        self.assertEqual(response_final.status_code, 200)
        self.assertEqual(response_final.json["resp"], "upload success")
        self.assertEqual(profile_avatar, "")

    def test_upload_txt_avatar(self):
        """test json response after uploading file not allowed as avatar(.txt)"""
        self.form["avatar"] = Upload("zoo.txt", b"zoo", "text/txt")

        response = self.form.submit()

        self.assertEqual(response.json["status_code"], 404)
        self.assertEqual(response.json["err"]["avatar"][0], self.err_file)

    def test_delete_button(self):
        """button delete should be present on detail profile"""

        but_del_profile = self.response.html.find("button", id="to_delete")

        self.assertEqual(self.response.status_code, 200)
        self.assertIsNotNone(but_del_profile)

    def test_on_delete_redirect(self):
        """redirect to home page after delete profile"""
        del_url = reverse("profiles:profile_delete", kwargs={"uuid": self.profile_uuid})
        home_url = reverse("home")

        resp = self.app.get(del_url)

        self.assertEqual(resp.status_code, 200)

        form = resp.forms["del_profile"]
        response = form.submit()

        self.assertRedirects(response, home_url)

    def test_delete_final_result(self):
        """request profile delete: username present on page;
        after profile delete: no trace of username"""
        del_url = reverse("profiles:profile_delete", kwargs={"uuid": self.profile_uuid})
        resp = self.app.get(del_url)

        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, self.user.username)

        form = resp.forms["del_profile"]
        response = form.submit().follow()

        self.assertEqual(response.status_code, 200)


@freeze_time("2024-12-25")
@override_settings(LANGUAGE_CODE="en", LANGUAGES=(("en", "English"),))
class NotificationsAdminTestCase(WebTest):
    def setUp(self) -> None:
        super().setUp()
        self.boze_user = UserFactory(username="boze anna", banned=True)
        self.app.set_user(self.boze_user)
        self.url = reverse(
            "profiles:profile_detail", kwargs={"uuid": self.boze_user.profile.uuid}
        )

    def test_change_count_unread_notifs(self):
        """profile datail page: show admin msg for banned user"""

        end_ban = date(2025, 1, 8)
        day = str(end_ban.day)
        year = str(end_ban.year)

        resp = self.app.get(self.url)

        admin_msg = resp.html.find("h5", class_="red")
        p = admin_msg.find_next_sibling()

        assert resp.status_code == 200
        assert admin_msg is not None
        assert year in p.text
        assert day in p.text
        assert "Jan" in p.text
