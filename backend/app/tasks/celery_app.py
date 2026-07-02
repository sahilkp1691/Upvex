from celery import Celery
from celery.schedules import crontab

from ..config import settings

celery_app = Celery(
    "upvex",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.tasks.generate", "app.tasks.streaks"],
)

celery_app.conf.update(
    task_always_eager=settings.celery_task_always_eager,
    task_eager_propagates=settings.celery_task_always_eager,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    beat_schedule={
        "evaluate-streaks-daily": {
            "task": "app.tasks.streaks.evaluate_streaks",
            "schedule": crontab(hour=0, minute=15),  # daily, shortly after UTC midnight
        },
    },
)
