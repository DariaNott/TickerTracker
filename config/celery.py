import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'check-ticker-prices-every-minute': {
        'task': 'trackers.tasks.check_ticker_price',
        'schedule': 60.0,  # seconds
    },
}