from django.contrib.auth import get_user_model
from django.test import override_settings
from django.urls import reverse
from django_webtest import WebTest

from src.accounts.tests.factories import UserFactory

User = get_user_model()


@override_settings(LANGUAGE_CODE="en", LANGUAGES=(("en", "English"),))
class AccountTestCase(WebTest):
    def setUp(self):
        super().setUp()
        self.url = reverse("account_signup")
        self.user = UserFactory.create()

        # initial request to get a form
        self.resp = self.app.get(self.url)

    def test_signup_form(self):
        """no new user if bot in form"""

        self.form = self.resp.forms["signup_form"]

        self.form["username"] = "Piggy"
        self.form["email"] = "iambot@mail.com"
        self.form["password1"] = "skiindiamons12345abc"
        self.form["password2"] = "skiindiamons12345abc"
        self.form["honeypot"].force_value("some abracadabra")
        self.form["agree_to_terms"] = True

        response = self.form.submit()

        count_users = User.objects.count()

        err_msg = "It should not be here"  # hidden field

        assert self.resp.status_code == 200
        assert response.status_code == 200
        assert count_users == 1
        assert err_msg in response.context["form"].errors["honeypot"]
