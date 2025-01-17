import logging

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin as LRM
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _
from django.views.generic import View

from .forms import ProfileForm
from .mixins import RestricProfileAccessMixin as RPM
from .models import Profile

logger = logging.getLogger("user_action")


class ProfileView(LRM, RPM, View):
    def get(self, request, **kwargs):
        uuid = kwargs.get("uuid")
        profile = get_object_or_404(Profile, uuid=uuid)
        form = ProfileForm(instance=profile)
        ctx = {"profile": profile, "form": form}
        return render(request, "profiles/profile_detail.html", ctx)

    def post(self, request, **kwargs):
        # check file ext on the client side

        uuid = kwargs.get("uuid")
        profile = get_object_or_404(Profile, uuid=uuid)
        form = ProfileForm(request.POST, request.FILES, profile)
        try:
            if form.is_valid():
                ava_img = form.cleaned_data.get("avatar")
                if ava_img:
                    profile.avatar = ava_img
                else:
                    profile.avatar = None
                profile.save()
                messages.success(request, _("You have changed your avatar"))
                logger.info(f"Success in update avatar {request.user}")
                return JsonResponse({"status_code": 200, "resp": "upload success"})
            else:
                logger.warning(f"Failed to update avatar {request.user}")
                return JsonResponse({"status_code": 404, "err": form.errors})
        except Exception as e:
            logger.error(f"upload failed in req {e}")


class ProfileDelete(LRM, RPM, View):
    """delete profile"""

    def get(self, request, **kwargs):
        ctx = {}
        uuid = kwargs.get("uuid")
        profile = get_object_or_404(Profile, uuid=uuid, user=request.user)
        ctx = {"profile": profile}
        return render(request, "profiles/profile_delete.html", ctx)

    def post(self, request, **kwargs):
        uuid = kwargs.get("uuid")
        profile = get_object_or_404(Profile, uuid=uuid, user=request.user)
        profile.delete()
        logger.warning(f"Profile deleted his {profile}")
        logout(request)
        request.session.flush()
        return redirect("home")
