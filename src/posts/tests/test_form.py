from django.test import override_settings
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django_webtest import WebTest


class PostWebTestCase(WebTest):
    @override_settings(LANGUAGE_CODE="ru", LANGUAGES=(("ru", "Russian"),))
    def test_search_lang_in_form(self):
        """check search form lang hidden field"""
        url = reverse("posts:search_posts")
        response = self.app.get(url)

        form = response.forms["search"]
        lang = form["lang"].value
        form["q"].value = "apple"

        response = form.submit()

        self.assertEqual(form.action, url)
        self.assertEqual(lang, "ru")
        self.assertEqual(response.status_code, 200)

    @override_settings(LANGUAGE_CODE="ru", LANGUAGES=(("ru", "Russian"),))
    def test_honeypot(self):
        """check honeypot field form;
        no form error rendered; instead div class=invalid-input"""
        url = reverse("home")
        response = self.app.get(url)

        form = response.forms["search"]
        form["q"] = "инфекция"
        form["first_honeypot"].force_value("some abracadabra")
        resp = form.submit()

        bot_msg = resp.html.find("div", class_="invalid-input")

        self.assertEqual(resp.status_code, 200)
        self.assertIsNotNone(bot_msg)

    @override_settings(LANGUAGE_CODE="en", LANGUAGES=(("en", "English"),))
    def test_empty_search_query(self):
        """check if user's search query was an empty string;
        no form error rendered; instead div class=empty-query"""
        url = reverse("home")
        response = self.app.get(url)

        form = response.forms["search"]
        form["q"] = ""
        resp = form.submit()

        empty_msg = resp.html.find("div", class_="empty-query")

        self.assertEqual(resp.status_code, 200)
        self.assertIsNotNone(empty_msg)
