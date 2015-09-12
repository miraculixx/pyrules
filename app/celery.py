'''
make sure Celery is correctly configured
see http://chriskief.com/2013/11/15/celery-3-1-with-django-django-celery-rabbitmq-and-macports/
'''
from __future__ import absolute_import

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')

from celery import Celery
from django.conf import settings 

app = Celery('app')
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS, related_name='tasks')
