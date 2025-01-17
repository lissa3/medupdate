import pytest
import time_machine

from src.contacts.models import NewsLetter

from .factories import NewsLetterFactory


class TestNewsLetter:
    @time_machine.travel("2023-07-17 00:00 +0000")
    def test_factory(self):
        """default letter status is PENDING"""
        letter = NewsLetterFactory()
        letter2 = NewsLetterFactory(letter_status=2)

        assert letter.title is not None
        assert letter.text is not None
        assert letter.letter_status == NewsLetter.Status.PENDING
        assert letter2.letter_status == NewsLetter.Status.SENT
