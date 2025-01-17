import logging
from datetime import date

from django.contrib.auth import get_user_model
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Profile

User = get_user_model()

logger = logging.getLogger("project")


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, *args, **kwargs):
    try:
        if created and instance.email:
            Profile.objects.get_or_create(user=instance)
            msg = f"Success to create profile user:{instance.id}"
            logger.info(msg)

    except Exception as e:
        msg = f"Failed to create profile,{e}"
        logger.warning(msg)


@receiver(post_delete, sender=Profile)
def set_user_inactive(sender, instance, **kwargs):
    """as profile deleted - user set to not activate")"""
    try:
        user_obj = instance.user
        user_obj.is_active = False
        user_obj.deactivated_on = date.today()
        user_obj.save()
        msg = f"success to make user {user_obj.id} inactive"
        logger.warning(msg)
    except Exception as e:
        msg = f"failed to make user {user_obj.id} inactive {e}"
        logger.warning(msg)
