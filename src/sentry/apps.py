import sentry_sdk
from django.apps import AppConfig
from django.conf import settings
from sentry_sdk.integrations.django import DjangoIntegration


def tracing(sampling_context):
    """Select a sample rate off of the requested path.

    To pevent bot's hitting root page and -= transtions count
    """
    path = sampling_context.get("wsgi_environ", {}).get("PATH_INFO", "")
    if path == "/":
        return 0

    return 1.0


class SentryConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "src.sentry"

    def ready(self):
        """created in separ app to prevent issues with circular imports"""

        if not settings.SENTRY_ENABLED:
            return
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            integrations=[DjangoIntegration()],
            traces_sample_rate=tracing,
            send_default_pii=True,
        )
