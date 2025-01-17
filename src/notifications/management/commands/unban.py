import logging

from django.core.management.base import BaseCommand
from django.utils import timezone

from src.contacts.exceptions import *
from src.notifications.models import Notification  # noqa
from src.profiles.models import Profile

logger = logging.getLogger("notifications")


class Command(BaseCommand):
    """
    un-ban banned users after 2 wks ban
    """

    help = "Unbanning users"  # noqa

    def handle(self, *args, **options):
        _date = timezone.localdate()
        str_date = _date.strftime("%A %d/%m/%Y")
        profiles_to_unban = Profile.objects.filter(end_ban__lte=_date)
        if profiles_to_unban.exists():
            unbanned_count = profiles_to_unban.count()
            for profile in profiles_to_unban:
                profile.start_ban = None
                profile.end_ban = None
                profile.admin_info = f"ban removed {str_date}"
                profile.save()
                profile.user.banned = False
                profile.user.save()
            msg = f"Un-banned {unbanned_count} users"
            logger.info(msg)
            # self.stdout.write(
            #     self.style.SUCCESS(f"Success; un-banned {unbanned_count} users")
            # )
        else:
            msg = "Found no users to unban"
            # self.stdout.write(self.style.SUCCESS(msg))
            logger.info(msg)
