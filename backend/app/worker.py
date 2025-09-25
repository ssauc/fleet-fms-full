from celery import Celery
import os
app = Celery("fleet", broker=os.environ.get("REDIS_URL", "redis://redis:6379/0"))
@app.task
def ping():
    return "pong"
