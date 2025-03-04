# Test fixtures
from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from backend.application.app import app
from backend.application.dependencies import get_celery_inspector_service, get_transactions_service
from backend.application.dto.transactions import AddTransactionDTO
from backend.logic.services.celery_inspector import CeleryInspectorService
from backend.logic.services.transaction import TransactionsService


@pytest.fixture
def mock_transactions_service(mocker):
    return mocker.AsyncMock(spec=TransactionsService)


@pytest.fixture
def mock_celery_inspector_service(mocker):
    return mocker.AsyncMock(spec=CeleryInspectorService)


@pytest.fixture
def test_client(mock_transactions_service, mock_celery_inspector_service) -> TestClient:
    # Override dependencies
    app.dependency_overrides[get_transactions_service] = lambda: mock_transactions_service
    app.dependency_overrides[get_celery_inspector_service] = lambda: mock_celery_inspector_service
    return TestClient(app)


@pytest.fixture
def sample_transactions() -> list[dict]:
    return [
        {
            "transaction_id": 1,
            "transaction_dttm": "2022-01-01T12:00:00",
            "customer_id": 1,
            "transaction_amt": 100.0,
        }
    ]
