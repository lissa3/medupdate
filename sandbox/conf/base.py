"""
django 4.2.1
"""
import os
from pathlib import Path

import environ
from django.utils.translation import gettext_lazy as _

from .conf_ckeditor import CKEDITOR_5_CONFIGS

# extra parent
BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env(
    ALLOWED_HOSTS=(list, []),
    ACCOUNT_DEFAULT_HTTP_PROTOCOL=(str, "https"),
    DEBUG=(bool, False),
    CSRF_COOKIE_SECURE=(bool, True),
    DATABASE_URL=(str, ""),
    DATABASE_SSL_REQUIRE=(bool, True),
    DATABASE_MAX_CONNECTION=(int, 600),
    EMAIl_BACKEND=(str, "anymail.backends.sendgrid.EmailBackend"),
    SECRET_KEY=(str, ""),
    SECURE_SSL_REDIRECT=(bool, True),
    SECURE_HSTS_SECONDS=(int, 60 * 60 * 24 * 365),  # one year in sec
    SENDGRID_FROM_EMAIL=(str, ""),
    SENTRY_ENABLED=(bool, True),
    SENDGRID_API_KEY=(str, ""),
    SESSION_COOKIE_SECURE=(bool, True),
    AWS_ACCESS_KEY_ID = (str,""),
    AWS_SECRET_ACCESS_KEY = (str,""),
    AWS_STORAGE_BUCKET_NAME = (str,"") ,
)
environ.Env.read_env(BASE_DIR / ".env")
DEBUG = True

SECRET_KEY = env("SECRET_KEY")
SITE_ID = 1
AUTH_USER_MODEL = "accounts.User"

ALLOWED_HOSTS: list[str] = env("ALLOWED_HOSTS")
DJANGO_APPS = [
    "modeltranslation",  # should be at the top
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django.contrib.postgres",
    "django.forms",
    "django.contrib.humanize",
    "django.contrib.sitemaps",
]

THIRD_PARTY = [
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "widget_tweaks",
    "django_htmx",
    "treebeard",
    "taggit",
    "django_ckeditor_5",
    "rosetta",
    "embed_video",
    "django_extensions",
]


LOCAL_APPS = [
    "src.accounts.apps.AccountsConfig",
    "src.profiles.apps.ProfilesConfig",
    "src.core.apps.CoreConfig",
    "src.posts.apps.PostsConfig",
    "src.contacts.apps.ContactsConfig",
    "src.comments.apps.CommentsConfig",
    "src.notifications.apps.NotificationsConfig",
]
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
]

ROOT_URLCONF = "sandbox.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "src" / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "src.notifications.context_processors.check_nofications",
                "src.contacts.context_processors.check_menu_data",
            ],
        },
    },
]

WSGI_APPLICATION = "sandbox.wsgi.application"

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


USE_I18N = True
LANGUAGE_CODE = "en"
LANGUAGES = (("en", _("English")), ("ru", _("Russian")), ("uk", _("Ukrainian")))
LOCALE_PATHS = (Path(BASE_DIR / "locale/"),)

TIME_ZONE = "UTC"
USE_TZ = True


#                extra's
# auto-slug (trans)
autoslug_modeltranslation_enable = True

# for custom clean widget
FORM_RENDERER = "django.forms.renderers.TemplatesSetting"

# email settings
ABSOLUTE_URL_BASE = "http://127.0.0.1:8000"
SENDGRID_API_KEY = env("SENDGRID_API_KEY")
EMAIl_BACKEND = env("EMAIl_BACKEND")
DEFAULT_FROM_EMAIL = "no-reply@medsandbox.com"
EMAIL_HOST = env("EMAIL_HOST")
EMAIL_HOST_USER = env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")

# img upload limits

MIN_UPLOAD_SIZE = 120  # in bytes
MAX_UPLOAD_SIZE = 1024 * 1024 * 2  # 2 MB
UPLOAD_FILE_TYPES = "image/jpeg,image/png,image/jpg"
FILE_UPLOAD_MAX_MEMORY_SIZE = 1024 * 1024 * 2  # for MemFileUploadHandler info


# allauth
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

ACCOUNT_FORMS = {
    "signup": "src.accounts.forms.CustomSignupForm",
}

ACCOUNT_USERNAME_REQUIRED = True
ACCOUNT_EMAIL_REQUIRED = True

ACCOUNT_AUTHENTICATION_METHOD = "email"  # can be both
ACCOUNT_EMAIL_VERIFICATION = "mandatory"  # "optional"
ACCOUNT_USERNAME_MIN_LENGTH = 3
LOGIN_REDIRECT_URL = "/"
LOGIN_URL = "/accounts/login"

# ACCOUNT_AUTHENTICATED_LOGIN_REDIRECTS = False
ACCOUNT_LOGOUT_REDIRECT_URL = "/"
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 5
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = True
ACCOUNT_EMAIL_SUBJECT_PREFIX = "Help  desk - "
ACCOUNT_USERNAME_BLACKLIST = ["admin", "administrator", "moderator"]
ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True


# taggit
TAGGIT_STRIP_UNICODE_WHEN_SLUGIFYING = True


# modeltranslation
MODELTRANSLATION_DEFAULT_LANGUAGE = "ru"
MODELTRANSLATION_LANGUAGES = (
    "ru",
    "en",
    "uk",
)

# sentry-sdk
SENTRY_ENABLED = False
SENTRY_DSN = "https://examplePublicKey@o0.ingest.sentry.io/0"
# logs

LOGGING_DIR = os.path.join(BASE_DIR, "logs")

# STATIC_ROOT = BASE_DIR / "src" / "static"
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR.joinpath("src", "static")]

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR.joinpath("media")

# aws s3: see deploy

# aws s3
AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME")
AWS_DEFAULT_ACL = "public-read"
AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=86400"}
PUBLIC_MEDIA_LOCATION = "media"
AWS_S3_FILE_OVERWRITE = False
AWS_QUERYSTRING_AUTH = False  # key will be not present in url
AWS_S3_MAX_MEMORY_SIZE = 2200000
AWS_S3_REGION_NAME = "eu-central-1"

DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"

AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME")

# celery + redis
CELERY_BROKER_URL = "redis://localhost:6379/0"
CELERY_ACCEPT_CONTENT = {"application/json"}
CELERY_RESULT_SERIALIZER = "json"
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_BACKEND = "django-db"
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unique-suffix",
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
# django-ckeditor
CKEDITOR_FILENAME_GENERATOR = "src.core.utils.base.file_generate_name"
CKEDITOR_5_FILE_STORAGE = "src.posts.storage.MediaStorage"
CKEDITOR_5_UPLOADS_FOLDER = "ckeditor5/"
CKEDITOR_5_UPLOAD_FILE_TYPES = ["jpg", "jpeg", "png", "webp"]
CKEDITOR_5_CONFIGS = CKEDITOR_5_CONFIGS
CKEDITOR_5_CUSTOM_CSS = "css/editor.css"  # optional

# logging
FORMATTERS = (
    {
        "standard": {
            "format": "{asctime}:{levelname} - {name} {module}.py \
                line:{lineno:d} {message}",
            "style": "{",
        },
        "simple": {"format": "{levelname} {name}{module}.py {message}", "style": "{"},
    },
)
HANDLERS = {
    "console": {
        "level": "INFO",
        "class": "logging.StreamHandler",
        "formatter": "simple",
    },
    "django": {
        "level": "INFO",
        "class": "logging.handlers.RotatingFileHandler",
        "formatter": "standard",
        "filename": os.path.join(LOGGING_DIR, "general.log"),
        "mode": "a",
        "maxBytes": 1024 * 1024,  # 2MB
        "backupCount": 5,
    },
    "project": {
        "level": "INFO",
        "class": "logging.handlers.RotatingFileHandler",
        "formatter": "standard",
        "filename": os.path.join(LOGGING_DIR, "project.log"),
        "mode": "a",
        "maxBytes": 1024 * 1024,  # 2MB
        "backupCount": 5,
    },
    "profile_action": {
        "level": "INFO",
        "class": "logging.FileHandler",
        "formatter": "standard",
        "filename": os.path.join(LOGGING_DIR, "upload_alert.log"),
    },
    "notifs": {
        "level": "INFO",
        "class": "logging.FileHandler",
        "formatter": "standard",
        "filename": os.path.join(LOGGING_DIR, "unbanned.log"),
    },
    "letter_celery": {
        "level": "DEBUG",
        "class": "logging.handlers.RotatingFileHandler",
        "formatter": "standard",
        "mode": "a",
        "maxBytes": 1024 * 1024,  # 2MB
        "backupCount": 5,
        "filename": os.path.join(LOGGING_DIR, "result_celery.log"),
    },
}
LOGGERS = (
    {
        "project": {
            "handlers": ["project"],
            "level": "INFO",
            "propagate": True,
        },
        "user_action": {
            "level": "INFO",
            "handlers": ["profile_action", "console"],
            "propagate": False,
        },
        "celery_tasks": {
            "level": "DEBUG",
            "handlers": ["letter_celery", "console"],
            "propagate": False,
        },
        "notifications": {"level": "INFO", "handlers": ["notifs"], "propagate": False},
        "root": {
            "handlers": ["django", "console"],
            "level": "WARNING",
        },
    },
)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
    },
    "formatters": FORMATTERS[0],
    "handlers": HANDLERS,
    "loggers": LOGGERS[0],
}
