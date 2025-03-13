from celery import Celery
from svc import settings

celery_app = Celery(
    __name__,
    broker=settings.REDIS_BROKER_URL,
    backend=settings.REDIS_RESULT_BACKEND,
)

celery_app.conf.timezone = "UTC"

celery_app.autodiscover_tasks(
    [
        "svc.celery.tasks.llama_task.insert_index_to_vector_db",
        "svc.celery.tasks.llama_task.query_index",
    ],
    force=True,
)

celery_app.conf.task_routes = {
    "svc.celery.tasks.llama_task.insert_index_to_vector_db": {
        "queue": "insert_index_to_vector_db_queue",
        "routing_key": "svc.celery.tasks.llama_task.insert_index_to_vector_db",
    },
    "svc.celery.tasks.llama_task.query_index": {
        "queue": "query_index_queue",
        "routing_key": "svc.celery.tasks.llama_task.query_index",
    }
}

celery_app.conf.broker_transport_options = {"retry_policy": {"timeout": 5.0}}
celery_app.conf.result_backend_transport_options = {"retry_policy": {"timeout": 5.0}}
