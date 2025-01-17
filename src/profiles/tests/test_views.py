import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.http import HttpRequest
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from src.accounts.tests.factories import UserFactory
from src.core.utils.base import get_temporary_image, get_temporary_text_file
from src.profiles.forms import ProfileForm
from src.profiles.models import Profile

User = get_user_model()

MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(LANGUAGE_CODE="ru", LANGUAGES=(("ru", "Russian"),))
@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class UploadImgTestCase(TestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        self.profile = Profile.objects.get(user=self.user)
        self.profile_uuid = self.profile.uuid
        self.url = reverse(
            "profiles:profile_detail", kwargs={"uuid": self.profile_uuid}
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)  # delete the temp dir
        super().tearDownClass()

    def test_auth_upload_and_remove_avatar(self):
        """Auth-ed user can first upload avatar;
        and remove it"""
        self.client.force_login(self.user)

        img_file = get_temporary_image()
        data_add_img = {"avatar": img_file}
        # upload avatar
        resp1 = self.client.post(self.url, data_add_img, format="multipart")
        self.profile.refresh_from_db()
        avatar_img = self.profile.avatar

        # removing avatar
        data_remove = {"avatar": ""}
        resp2 = self.client.post(self.url, data_remove, format="multipart")
        self.profile.refresh_from_db()

        self.assertEqual(resp1.status_code, 200)
        self.assertEqual(resp2.status_code, 200)
        self.assertIsNotNone(avatar_img)
        self.assertEqual(self.profile.avatar.name, "")

    def test_auth_upload_avatar(self):
        """Auth-ed user can upload an image"""
        self.client.force_login(self.user)
        initial_avatar = self.profile.avatar
        img_file = get_temporary_image()
        data = {"avatar": img_file}
        #  post request with an img file(allowed)
        resp = self.client.post(self.url, data, format="multipart")

        self.profile.refresh_from_db()
        final_avatar = self.profile.avatar

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(initial_avatar.name, "")
        self.assertIsNotNone(final_avatar.size)
        self.assertNotEqual(final_avatar.name, "")
        self.assertNotEqual(final_avatar.url, "")

    def test_fail_not_auth_upload_avatar(self):
        """Not auth user can not upload an image"""
        profile_uuid = self.profile.uuid
        img_file = get_temporary_image()
        data = {"avatar": img_file}
        to_login_url = f"/accounts/login?next=/ru/profile/{profile_uuid}/"

        #  post request with an img file(allowed)
        resp = self.client.post(self.url, data, format="multipart", follow=True)

        self.profile.refresh_from_db()
        final_avatar = self.profile.avatar

        next_page, status_code = resp.redirect_chain[0]

        self.assertEqual(status_code, 302)
        self.assertEqual(next_page, to_login_url)
        self.assertEqual(final_avatar.name, "")

    def test_fail_auth_upload_text_file_instead_img(self):
        """
        Auth-ed user can NOT upload an .txt file(not allowed) as an avatar;
        avatar attr not updated
        """
        self.client.force_login(self.user)
        initial_avatar = self.profile.avatar
        text_file = get_temporary_text_file()
        # error_message = "Upload a valid image. The file you \
        # uploaded was either not an image or a corrupted image."

        resp = self.client.post(
            self.url, {"avatar": text_file}, format="multipart", follow=True
        )
        resp_dict = resp.json()
        self.profile.refresh_from_db()
        final_avatar = self.profile.avatar

        self.assertEqual(resp_dict["status_code"], 404)
        # self.assertEqual(resp_dict["err"]["avatar"][0], error_message)
        self.assertEqual(initial_avatar.name, "")
        self.assertEqual(final_avatar.name, "")

    def test_empty_profile_form(self):
        """check empty form field avatar with help text"""

        help_text = "Size not more than 2 MB; format:png/jpeg/jpg"
        form = ProfileForm()

        self.assertIn("avatar", form.fields)
        self.assertTrue(form["avatar"].help_text, help_text)

    def test_form_err_extention_not_allowed(self):
        """
        Auth-ed user can NOT upload an .txt file(not allowed)
        as an avatar; raise arror
        """

        text_file = get_temporary_text_file()
        err_msg = _(
            "Upload a valid image. The file you uploaded was either not \
            an image or a corrupted image."
        )
        request = HttpRequest()
        request.POST = {}
        request.FILES = {"avatar": text_file}
        form = ProfileForm(request.POST, request.FILES)
        self.assertTrue(form.is_bound)
        self.assertTrue(form.is_multipart)
        self.assertFalse(form.is_valid())
        self.assertTrue(form.fields["avatar"].error_messages["invalid_image"], err_msg)

    def test_form_allowed_extention(self):
        """
        Auth-ed user can upload an file with allowed ext;
        """

        png_file = get_temporary_image()
        request = HttpRequest()
        request.POST = {}
        request.FILES = {"avatar": png_file}
        form = ProfileForm(request.POST, request.FILES)

        self.assertTrue(form.is_bound)
        self.assertTrue(form.is_multipart)
        self.assertTrue(form.is_valid())


@override_settings(LANGUAGE_CODE="en", LANGUAGES=(("en", "English"),))
@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class ProfileNotFoundTestCase(TestCase):
    def test_failure_profile_404(self):
        """Profile is not found"""
        user = UserFactory()
        self.client.force_login(user)
        self.url = "/profile/12345/"  # does not exist

        img_file = get_temporary_image()
        data_add_img = {"avatar": img_file}
        # upload avatar
        resp = self.client.post(self.url, data_add_img, format="multipart")

        self.assertEqual(resp.status_code, 404)
