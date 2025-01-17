import logging
from smtplib import SMTPException

# from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import mail
from django.template.loader import render_to_string
from django.utils import timezone

from src.contacts.exceptions import *  # noqa
from src.contacts.models import NewsLetter
from src.posts.models.post_model import Post
from src.profiles.models import Profile

User = get_user_model()

logger = logging.getLogger("celery_logger")


# @shared_task
def send_letter():
    """send news letter"""
    logger.warning("greet to tata")

    _date = timezone.localdate()
    str_date = _date.strftime("%d/%m/%Y")
    stamp = f"Newsletter {_date:%A}, {_date:%b}. {_date:%d} {str_date}"
    domain = settings.ABSOLUTE_URL_BASE
    profiles = Profile.objects.select_related("user").send_news()
    letter = NewsLetter.objects.filter(letter_status=1).last()
    ctx = {"letter": letter, "domain": domain}
    if profiles and letter:
        try:
            posts = Post.objects.get_public().filter(send_status=1, letter=letter)
            ctx.update({"posts": posts})
            for profile in profiles:
                ctx.update({"uuid": profile.uuid})
                text_msg = render_to_string("contacts/emails/letter.txt", ctx)
                html_msg = render_to_string("contacts/emails/letter.html", ctx)
                mail.send_mail(
                    subject=stamp,
                    message=text_msg,
                    html_message=html_msg,
                    from_email="noreply-newsletter@dmain.com",
                    recipient_list=[profile.user.email],
                )
            letter.date_sent = timezone.now()
            letter.letter_status = 2
            letter.save()
            if posts.count() > 0:
                for post in posts:
                    post.send_status = 2
                    post.save()
            logger.info(f"OK send news to: {profiles.count()} users.")
        except SMTPException as e:
            msg = f"failed to send news smtp exception {e}"  # noqa
            logger.warning(msg)
        except Exception as e:  # noqa
            msg = f"failed to send news,{e}"  # noqa
            logger.warning(msg)
    else:
        if not profiles:
            logger.warning("no users wishing news")
            raise NewsFansNotFoundException("No profiles not send news")
        elif not letter:
            logger.warning("no letter to send")
            raise LetterNotFoundException("No letter to send")
