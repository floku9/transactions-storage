from celery import Celery

from settings import celery_settings, redis_settings

app = Celery(
    celery_settings.CELERY_APP_NAME,
    broker=redis_settings.REDIS_URL,
    result_backend=redis_settings.REDIS_URL,
)

app.conf.task_serializer = "json"
app.conf.result_serializer = "json"
app.conf.accept_content = ["json"]
app.conf.task_track_started = True
app.conf.task_time_limit = 3600

app.conf.task_default_queue = celery_settings.CELERY_QUEUE_NAME
