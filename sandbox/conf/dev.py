from .base import *  # noqa

INTERNAL_IPS = ["127.0.0.1"]
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
ABSOLUTE_URL_BASE = "http://127.0.0.1:8000"
EMAIL_HOST = "some-host"
EMAIL_HOST_USER = "some-user"
EMAIL_HOST_PASSWORD = "supersecret"

INSTALLED_APPS += []
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": env("DB_NAME"),
        "USER": env("DB_USER"),
        "PASSWORD": env("DB_PSW"),
        "HOST": "localhost",
        "PORT": "5432",
    }
}

DEFAULT_FILE_STORAGE = "django.core.files.storage.memory.InMemoryStorage"
