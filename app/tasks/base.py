from app.worker import celery_app


@celery_app.task(bind=True)
def test_task(self):
    """
    Test task to verify Celery is working
    """
    return {"status": "Celery is working!"}
