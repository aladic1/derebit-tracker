from celery_app import celery_app

# Регистрируем задачу
@celery_app.task(name="fetch_prices_task", bind=True)
def fetch_prices_task_wrapper(self):
    """Wrapper for the fetch prices task."""
    from app.tasks.fetch_prices import fetch_prices_task
    return fetch_prices_task()
