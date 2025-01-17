import logging

from django.core.management.base import BaseCommand
from django.utils import timezone

from src.contacts.exceptions import *
from src.core.tasks import post_letter

logger = logging.getLogger("celery_tasks")


class Command(BaseCommand):
    """
    sending news letter
    """

    help = "send news letter"  # noqa

    def handle(self, *args, **options):
        _date = timezone.localdate()
        str_date = _date.strftime("%A %d/%m/%Y")
        try:
            post_letter()
            # post_letter.delay()  for celery if activated
            msg = f"News letter sent, {str_date}"
            logger.info(msg)
            self.stdout.write(self.style.SUCCESS("Success in sending letter"))
        except Exception as e:
            msg = f"Failed to send news letter,{e}"
            self.stdout.write(self.style.ERROR(msg))
            logger.error(msg)
