from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin as LRM
from django.core.mail import send_mail
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.template.loader import get_template
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import View
from django.views.generic.edit import FormView

from src.contacts.forms import ContactForm
from src.profiles.models import Profile

from .exceptions import HtmxFailureError


class Subscribe(LRM, View):
    def get(self, request):
        """
        only auth users can subscribe to a news letter
        via menu dropdown item
        """
        return render(
            request,
            "contacts/subscription/confirmation.html",
        )

    def post(self, request, **kwargs):
        """
        htmx_based request with redirect to home page
        and flash msg as a feedback
        """
        htmx_req = request.headers.get("hx-request")
        try:
            if request.user.is_authenticated and htmx_req is not None:
                _id = request.user.profile.id
                profile = get_object_or_404(Profile, id=_id)
                messages.success(request, _("You have subscribed to the news letter"))
                profile.want_news = True
                profile.save()
                return HttpResponse(
                    headers={
                        "HX-Redirect": "/",
                    },
                )
            elif htmx_req is None:
                raise HtmxFailureError(_("Subscription failed"))
        except HtmxFailureError:
            raise

        return HttpResponseRedirect("/")


class UnSubscribe(View):
    def get(self, request, **kwargs):
        """
        link in newsletter contains profile uuid
        """
        uuid = kwargs.get("uuid")

        profile = get_object_or_404(Profile, uuid=uuid)
        ctx = {"uuid": profile.uuid}
        return render(request, "contacts/subscription/unsubscribe.html", ctx)

    def post(self, request, **kwargs):
        # htmx_based
        htmx_req = request.headers.get("hx-request")
        try:
            uuid = kwargs.get("uuid")
            profile = get_object_or_404(Profile, uuid=uuid)
            if htmx_req and profile:
                messages.success(request, _("You have unsubscribed to the news letter"))
                profile.want_news = False
                profile.save()
                return HttpResponse(
                    headers={
                        "HX-Redirect": "/",
                    },
                )
            elif htmx_req is None:
                raise HtmxFailureError(_("Something went wrong.Can't unsubscribe."))
        except HtmxFailureError:
            raise

        return HttpResponseRedirect("/")


class ContactView(FormView):
    """unauth or auth user can send a feedback to admin"""

    template_name = "contacts/feedback/feedback.html"
    form_class = ContactForm
    success_url = reverse_lazy("home")

    def get_form_kwargs(self) -> dict:
        kwargs = super().get_form_kwargs()
        if self.request.user.is_authenticated:
            kwargs.update(
                {
                    "initial": {
                        "name": self.request.user.username,
                        "email": self.request.user.email,
                    }
                }
            )
        return kwargs

    def form_valid(self, form):
        name = form.cleaned_data.get("name")
        email = form.cleaned_data.get("email")
        subject = form.cleaned_data.get("subject")
        message = form.cleaned_data.get("message")
        context = {
            "user": name,
            "subject": subject,
            "email": email,
            "message": message,
        }

        from_email = email
        to_email = ("some-mail@mail.com",)
        contact_message = get_template("contacts/feedback/contact_msg.txt").render(
            context
        )

        # self.send_mail_to_admin() ?
        send_mail(subject, contact_message, from_email, to_email, fail_silently=True)

        messages.add_message(
            self.request,
            messages.SUCCESS,
            _("Your message is sent"),
        )

        return HttpResponseRedirect(redirect_to=self.success_url)
