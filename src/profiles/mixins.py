import logging

from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from .models import Profile

logger = logging.getLogger("user_action")


class RestricProfileAccessMixin:
    """restrict access to profile only to the profile owner"""

    def dispatch(self, request, *args, **kwargs):
        uuid = self.kwargs.get("uuid")
        profile = get_object_or_404(Profile, uuid=uuid)
        if not (
            request.user.is_authenticated and request.user.profile.uuid == profile.uuid
        ):
            logger.warning(
                f"User  {self.request.user} violates restr for profile {uuid}"
            )
            raise PermissionDenied("You do not have enough permission to see this page")

        return super().dispatch(request, *args, **kwargs)
