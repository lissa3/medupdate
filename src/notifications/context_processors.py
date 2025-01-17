from src.notifications.models import Notification


def check_nofications(request):
    """
    Auth user will see in UI(menu) count unread notifications:
    admin msg + comments replies
    """
    if request.user.is_authenticated:
        notifs = Notification.objects.all_unread_notifics(
            recipient=request.user
        ).count()
    else:
        notifs = None
    return {"notifs": notifs}
