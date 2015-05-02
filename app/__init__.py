from __future__ import absolute_import
 
# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
# see http://chriskief.com/2013/11/15/celery-3-1-with-django-django-celery-rabbitmq-and-macports/
from .celery import app 
