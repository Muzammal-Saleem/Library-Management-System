import os
from celery import Celery

# Redis configuration URL
redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")

celery_app = Celery(
    "library_tasks",
    broker=redis_url,
    backend=redis_url
)

# Celery configurations
celery_app.conf.update(
    task_track_started=True,
    result_expires=3600,  # Keep results for 1 hour
)

# Automatically discover tasks in app package modules
celery_app.autodiscover_tasks(["app"])
