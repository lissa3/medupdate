from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.utils.translation import gettext_lazy as _

from src.contacts.exceptions import HtmxFailureError
from src.notifications.models import Notification


@login_required
def show_unread_notifs(request):
    """htmx: list of all unread notifs"""
    unread_notifs = Notification.objects.all_unread_notifics(request.user)
    ctx = {"user_notifications": unread_notifs}
    return render(request, "notifications/unread_notifs.html", ctx)


@login_required
def get_top(request):
    """
    htmx: last top notification: replied comments
    + and evt admin msg(ban)
    """
    ctx = {"show_more": False}
    top_notifs = Notification.objects.get_top(request.user)
    if top_notifs:
        ctx.update({"top_notifs": top_notifs})
        count_all_unread = Notification.objects.count_unread_notifics(request.user)
        if count_all_unread > top_notifs.count():
            ctx.update({"show_more": True})
    from_admin = Notification.objects.filter(
        from_admin=True, read=False, recipient=request.user
    ).exists()
    if from_admin:
        admin_ban_msg = Notification.objects.filter(from_admin=True, read=False).last()
        if admin_ban_msg and not admin_ban_msg.read:
            ctx.update({"admin_msg": admin_ban_msg})
    return render(request, "notifications/menu_notifs.html", ctx)


@login_required
def make_notifs_read(request, notif_id=None):
    """
    two urls - one function:separate options:
    notif admin msg (about ban) and  reply notifs;
    """
    if request.htmx and request.method == "POST":
        path_to_go = request.headers["Referer"]
        if notif_id is not None:
            # make admin msg read
            notif = get_object_or_404(Notification, id=notif_id)
            notif.read = True
            notif.save()
        else:
            # make notifs comment replies  read
            Notification.objects.make_all_read(request.user)
        return HttpResponse(
            headers={
                "HX-Redirect": path_to_go,
            },
        )
    else:
        raise HtmxFailureError(_("Something went wrong.Please try later"))
