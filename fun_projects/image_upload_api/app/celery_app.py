from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "image_upload_api",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks"],
)
celery_app.conf.task_track_started = True
