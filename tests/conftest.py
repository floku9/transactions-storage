import pytest
from celery import Celery


@pytest.fixture
def mock_celery():
    celery = Celery("test_app")
    celery.conf.update(
        broker_url="memory://",
        result_backend="cache+memory://",
        task_always_eager=True,
    )
    return celery


@pytest.fixture(scope="session")
def celery_config():
    return {
        "broker_url": "memory://",
        "result_backend": "cache+memory://",
        "task_always_eager": True,
    }
