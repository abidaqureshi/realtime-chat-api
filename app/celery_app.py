from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "chat_worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks.notification_tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60
)

celery_app.conf.beat_schedule = {
    'cleanup-old-sessions-every-hours': {
        'task': 'app.task.notification_tasks.cleanup_old_sessions',
        'schedule': 3600.0,
    }
}