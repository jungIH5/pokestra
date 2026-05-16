import os
from celery import Celery

celery_app = Celery("photo_maestro")

celery_app.conf.update(
    broker_url=os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0"),
    result_backend=os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/1"),
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_track_started=True,
    worker_prefetch_multiplier=1,  # 무거운 ML 작업이라 한 번에 하나씩
    task_routes={"worker.run_analysis_task": {"queue": "analysis"}},
)
