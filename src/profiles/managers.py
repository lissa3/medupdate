from django.db.models import QuerySet


class ProfileManager(QuerySet):
    def send_news(self):
        """
        subscription is only for active users;
        unscubscribed:
        - user deleted account |=> no profile| no  letter
        - user still active + profile|=> via a link in email
          letter
        """
        return self.select_related("user").filter(user__is_active=True, want_news=True)
