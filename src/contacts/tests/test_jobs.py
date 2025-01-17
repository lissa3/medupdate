import tempfile

import time_machine
from django.conf import settings
from django.core import mail
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse

from src.contacts.exceptions import *  # noqa
from src.contacts.management.commands import send_news
from src.contacts.models import NewsLetter
from src.posts.models.post_model import Post
from src.posts.tests.factories import PostFactory
from src.profiles.tests.factories.profile_factory import ProfileFactory

from .factories import NewsLetterFactory

MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(LANGUAGE_CODE="ru", LANGUAGES=(("ru", "Russian"),))
class TestSendEmailJob(TestCase):
    @time_machine.travel("2023-07-17 00:00 +0000")
    def test_send_news_with_posts_links(self):
        """
        active user (can) get news letter via email
        with corresp links to posts;
        if sending OK: letter and related posts
        change their status
        email (html)text contains a link to unsubscribe
        """
        subject = "Newsletter Monday, Jul. 17 17/07/2023"
        profile = ProfileFactory(want_news=True)
        domain = settings.ABSOLUTE_URL_BASE
        letter = NewsLetterFactory(letter_status=1)
        post = PostFactory(send_status=1, status=2, letter=letter, title_ru="заголовок")
        post_title = post.title_ru

        short_url = reverse("contacts:end_news", kwargs={"uuid": profile.uuid})
        full_link_unsub = f"{domain}{short_url}"
        call_command("send_news")

        self.assertEqual(len(mail.outbox), 1)

        sent_mail = mail.outbox[0]
        html_msg = sent_mail.alternatives[0][0]

        self.assertTrue(sent_mail.to == [profile.user.email])
        self.assertTrue(sent_mail.subject == subject)

        self.assertTrue(letter.text in sent_mail.body)
        self.assertTrue(letter.text in html_msg)

        self.assertIn(post_title, sent_mail.body)
        self.assertIn(post_title, html_msg)
        self.assertIn(full_link_unsub, sent_mail.body)
        self.assertIn(full_link_unsub, html_msg)

        # after sending

        post_after = Post.objects.filter(send_status=2).last()
        letter_after = NewsLetter.objects.filter(letter_status=2).last()

        self.assertEqual(post.id, post_after.id)
        self.assertEqual(post_after.send_status, 2)
        self.assertEqual(letter.id, letter_after.id)
        self.assertEqual(letter_after.letter_status, 2)

    @time_machine.travel("2023-07-17 00:00 +0000")
    def test_send_news_no_posts(self):
        """
        No posts links in the letter no posts with
        send_status
        email (html)text contains a link to unsubscribe
        """
        subject = "Newsletter Monday, Jul. 17 17/07/2023"
        profile = ProfileFactory(want_news=True)
        post = PostFactory(send_status=0, title_ru="слон")
        post_title = post.title_ru
        # domain = settings.ABSOLUTE_URL_BASE
        letter = NewsLetterFactory(letter_status=1)

        # short_url = reverse("contacts:end_news", kwargs={"uuid": profile.uuid})
        # full_link_unsub = f"{domain}{short_url}"
        call_command("send_news")

        self.assertEqual(len(mail.outbox), 1)

        sent_mail = mail.outbox[0]
        html_msg = sent_mail.alternatives[0][0]

        self.assertTrue(sent_mail.to == [profile.user.email])
        # self.assertTrue(sent_mail.to == [settings.DEFAULT_FROM_EMAIL])
        self.assertTrue(sent_mail.subject == subject)

        self.assertTrue(letter.text in sent_mail.body)
        self.assertTrue(letter.text in html_msg)
        self.assertNotIn(post_title, sent_mail.body)
        self.assertNotIn(post_title, html_msg)

        # after sending
        post_after = Post.objects.filter(send_status=2).count()
        letter_after = NewsLetter.objects.filter(letter_status=2).last()

        self.assertEqual(post_after, 0)
        self.assertEqual(letter.id, letter_after.id)
        self.assertEqual(letter_after.letter_status, 2)
        self.assertEqual(letter_after.letter_status, 2)
        self.assertEqual(letter_after.letter_status, 2)
        self.assertEqual(letter_after.letter_status, 2)
