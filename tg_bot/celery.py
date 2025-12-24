import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("config")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "send-test-notification-every-minute": {
        "task": "tg_bot.tasks.send_test_notification",
        "schedule": 60.0,
    },
}
