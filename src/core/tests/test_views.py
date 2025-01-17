# from unittest.mock import patch

from django.test import TestCase, override_settings
from django.urls import reverse


@override_settings(LANGUAGE_CODE="uk", LANGUAGES=(("uk", "Ukrainian"),))
class HomePageTest(TestCase):
    """test home and intro view"""

    # @patch("src.posts.models.media_model.Video")
    # def test_home_page(self, mock_video):
    def test_home_page(self):
        """home"""
        # mock_video.url = "https://abracadabra.com"
        url = reverse("home")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    # @patch("src.posts.models.media_model.Video")
    # def test_problem_present_page(self, mock_video):
    def test_problem_present_page(self):
        """page problem presentation"""
        # mock_video.url = "https://abracadabra.com"
        url = reverse("core:problem_present")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
