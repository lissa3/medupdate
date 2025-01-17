from django.test import override_settings
from django.urls import reverse
from django_webtest import WebTest

from src.accounts.admin import User
from src.accounts.tests.factories import AdminSupUserFactory, UserFactory


@override_settings(LANGUAGE_CODE="en", LANGUAGES=(("en", "English"),))
class TestAdminCategoryForm(WebTest):
    def setUp(self):
        self.super_user = AdminSupUserFactory()
        self.user = UserFactory(username="anna", email="anna@mail.com")
        self.app.set_user(self.super_user)

    def test_change_user(self):
        """logged super user can ban another user via admin UI"""
        start_not_banned = self.user.banned
        url = reverse("admin:accounts_user_change", kwargs={"object_id": self.user.id})
        resp = self.app.get(url=url)

        self.assertEqual(resp.status_code, 200)

        form = resp.forms["user_form"]
        form["banned"] = True

        response = form.submit()

        user_banned = User.objects.get(id=self.user.id).banned

        self.assertEqual(response.status_code, 302)
        self.assertFalse(start_not_banned)
        self.assertTrue(user_banned)
