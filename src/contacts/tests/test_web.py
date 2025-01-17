from django.test import override_settings
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django_webtest import WebTest

from src.accounts.tests.factories import UserFactory


@override_settings(LANGUAGE_CODE="en", LANGUAGES=(("en", "English"),))
class SubscribeLinkTest(WebTest):
    """only auth users can subscribe for a newsletter"""

    def setUp(self):
        super().setUp()
        self.user = UserFactory()
        self.url = reverse("home")

    def test_auth_user_has_subscr_link_in_menu(self):
        """Auth user has link for a newsletter"""
        self.app.set_user(self.user)
        self.response = self.app.get(self.url)
        self.assertEqual(self.response.status_code, 200)

        subs_link = self.response.html.find("a", id="subLink")

        self.assertIsNotNone(subs_link)

    def test_unauth_user_no_link_in_menu(self):
        """Unauth user has no link in menu for a newsletter"""

        self.response = self.app.get(self.url)
        self.assertEqual(self.response.status_code, 200)

        subs_link = self.response.html.find("a", id="subLink")

        self.assertIsNone(subs_link)


@override_settings(LANGUAGE_CODE="ru", LANGUAGES=(("ru", "Russian"),))
class ContactFormTest(WebTest):
    def setUp(self):
        super().setUp()
        self.url = reverse("contacts:feedback")
        self.user = UserFactory(username="Snork", email="jaga@mail.com")

    def test_contact_form_auth_user(self):
        """auth loggen in user's form is pre-filled with name and mail"""
        self.app.set_user(self.user)
        response = self.app.get(self.url)
        self.assertEqual(response.status_code, 200)

        form = response.forms["feedback"]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(form["name"].value, "Snork")
        self.assertEqual(form["email"].value, "jaga@mail.com")

    def test_contact_form_valid(self):
        response = self.app.get(self.url)
        self.assertEqual(response.status_code, 200)

        form = response.forms["feedback"]
        form["name"] = "Hemul"
        form["subject"] = "collection"
        form["email"] = "hemul@mail.com"
        form["message"] = "Some text for feedback"

        resp = form.submit().follow()
        messages = list(resp.context["messages"])

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), _("Your message is sent"))

    def test_contact_form_honeypot(self):
        response = self.app.get(self.url)
        self.assertEqual(response.status_code, 200)

        form = response.forms["feedback"]
        form["name"] = "Hemul"
        form["subject"] = "collection"
        form["email"] = "hemul@mail.com"
        form["message"] = "Some text for feedback"
        form["honeypot"] = "Bot is here"

        resp = form.submit()
        messages = list(resp.context["messages"])

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(messages), 0)
        self.assertEqual(
            resp.context["form"].errors, {"honeypot": [_("It should not be here")]}
        )

    def test_failure_too_short_msg(self):
        """failure if msg too short"""

        response = self.app.get(self.url)
        form = response.forms["feedback"]
        form["name"] = "Hemul"
        form["subject"] = "collection"
        form["email"] = "hemul@mail.com"
        form["message"] = "abc"

        response = form.submit()
        msg_txt = _("Your message is too short; should contain at least two words")

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            response.context["form"].errors,
            {"message": [msg_txt]},
        )
