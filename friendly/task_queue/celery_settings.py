from datetime import timedelta

from celery import Celery
from config import settings

celery = Celery(__name__, backend=settings.REDIS_URL, broker=settings.REDIS_URL)
celery.conf.broker_connection_retry_on_startup = True
celery.autodiscover_tasks(["mail", "firebase"])

celery.conf.update(result_expires=timedelta(hours=1))
