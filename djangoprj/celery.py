# from __future__ import absolute_import, unicode_literals

import os

from celery import Celery
from celery.schedules import crontab


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangoprj.settings')
app = Celery('djangoprj')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


app.conf.beat_schedule = {
    'import-daily-at-2am': {
        'task': 'create_fixture_install',
        'schedule': crontab(hour=2, minute=0)
    },
}
