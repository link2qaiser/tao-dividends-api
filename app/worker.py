# app/tasks/worker.py
from celery import Celery
from app.core.config import settings
import os

celery_app = Celery(
    "worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

# Configure Celery
celery_app.conf.task_routes = {
    "app.tasks.*": {"queue": "default"},
    "process_sentiment_stake": {"queue": "blockchain"},
}

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=600,  # 10 minutes
    worker_prefetch_multiplier=1,  # Process one task at a time
)
