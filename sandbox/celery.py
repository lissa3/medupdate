# from __future__ import absolute_import, unicode_literals
# import os
# from celery import Celery
# from django.conf import settings

# # should be same name as you folder with settings

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sandbox.settings")

# app = Celery('sanbox',broker='redis://localhost')
# app.config_from_object('django.conf:settings', namespace='CELERY')
# app.conf.broker_connection_retry_on_startup = True

# app.autodiscover_tasks()
