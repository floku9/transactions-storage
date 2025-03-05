# Test fixtures

import pytest
from fastapi.testclient import TestClient

from backend.application.app import app
from backend.application.dependencies import (
    get_celery_inspector_service,
    get_transactions_celery_service,
    get_transactions_db_service,
)
from backend.logic.services.celery_inspector import CeleryInspectorService
from backend.logic.services.transaction import TransactionsCeleryService, TransactionsDBService


@pytest.fixture
def mock_transactions_db_service(mocker):
    return mocker.AsyncMock(spec=TransactionsDBService)


@pytest.fixture
def mock_transactions_celery_service(mocker):
    return mocker.AsyncMock(spec=TransactionsCeleryService)


@pytest.fixture
def mock_celery_inspector_service(mocker):
    return mocker.AsyncMock(spec=CeleryInspectorService)


@pytest.fixture
def test_client(
    mock_transactions_db_service, mock_celery_inspector_service, mock_transactions_celery_service
) -> TestClient:
    # Override dependencies
    app.dependency_overrides[get_transactions_db_service] = lambda: mock_transactions_db_service
    app.dependency_overrides[get_celery_inspector_service] = lambda: mock_celery_inspector_service
    app.dependency_overrides[get_transactions_celery_service] = (
        lambda: mock_transactions_celery_service
    )
    return TestClient(app)


@pytest.fixture
def sample_transactions() -> list[dict]:
    return [
        {
            "transaction_id": 5,
            "transaction_dttm": "2022-01-01T12:00:00",
            "customer_id": 1,
            "transaction_amt": 100.0,
        }
    ]
