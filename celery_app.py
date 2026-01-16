from celery import Celery
from app.core.config import settings

# Создаем экземпляр Celery с другим именем файла
celery_app = Celery(
    "deribit_tracker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks.fetch_prices"]  # Явно указываем задачи
)

# Настройки
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    broker_connection_retry_on_startup=True,
)

# Расписание для периодических задач
celery_app.conf.beat_schedule = {
    "fetch-prices-every-minute": {
        "task": "app.tasks.fetch_prices.fetch_prices_task",
        "schedule": 60.0,  # Каждые 60 секунд
    },
}

# Регистрируем задачу явно
from app.tasks.fetch_prices import fetch_prices_task as fetch_prices_func

@celery_app.task(name="app.tasks.fetch_prices.fetch_prices_task")
def fetch_prices_task():
    """Celery task wrapper."""
    return fetch_prices_func()

# Также регистрируем под коротким именем для совместимости
@celery_app.task(name="fetch_prices_task")
def fetch_prices_task_short():
    """Celery task wrapper with short name."""
    return fetch_prices_func()