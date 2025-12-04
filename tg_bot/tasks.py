from celery import shared_task
import logging

logger = logging.getLogger(__name__)

@shared_task
def send_test_notification():
    """Тестовая задача для проверки Celery"""
    logger.info("Celery задача выполнена: тестовое уведомление")
    return "Тестовое уведомление отправлено"