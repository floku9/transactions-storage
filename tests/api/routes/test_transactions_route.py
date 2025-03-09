import json

from fastapi.testclient import TestClient
from mock import AsyncMock, patch
from redis import Redis

from backend.application.dto.transactions import GetTransactionDTO
from utils.messages import APIErrorMessages


def test_add_transactions_success(
    test_client: TestClient,
    mock_transactions_db_service: AsyncMock,
    mock_transactions_celery_service: AsyncMock,
    sample_transactions: list[dict],
    test_redis_client: Redis,
):
    # Arrange
    mock_transactions_db_service.add_to_db.return_value = None
    mock_transactions_celery_service.add_to_celery.return_value = "task-123"
    mock_transactions_db_service.get_many_by_id.return_value = None

    queue_name = "test_queue"
    # Act
    with patch(
        "backend.application.routes.transactions.celery_settings.CELERY_QUEUE_NAME", queue_name
    ):
        # Act
        response = test_client.post("/transactions/add", json=sample_transactions)

    # Assert
    assert response.status_code == 202
    assert response.json() == "task-123"
    assert mock_transactions_db_service.add_to_db.assert_called_once
    assert mock_transactions_celery_service.add_to_celery.assert_called_once


def test_add_transactions_celery_busy(
    test_client: TestClient,
    mock_transactions_db_service: AsyncMock,
    mock_transactions_celery_service: AsyncMock,
    test_redis_client: Redis,
    sample_transactions: list[dict],
):
    queue_name = "test_queue"
    task1 = {"task_id": "task1", "body": "some_work"}
    test_redis_client.lpush(queue_name, json.dumps(task1))

    # Act
    with patch(
        "backend.application.routes.transactions.celery_settings.CELERY_QUEUE_NAME", queue_name
    ):

        # Act
        response = test_client.post("/transactions/add", json=sample_transactions)

    # Assert
    assert response.status_code == 429
    assert response.json()["detail"] == APIErrorMessages.CELERY_IS_BUSY
    assert mock_transactions_db_service.add_to_db.assert_not_called
    assert mock_transactions_celery_service.add_to_celery.assert_not_called


def test_transactions_already_in_db(
    test_client: TestClient,
    mock_transactions_db_service: AsyncMock,
    mock_transactions_celery_service: AsyncMock,
    sample_transactions: list[dict],
):
    mock_transactions_db_service.get_many_by_id.return_value = [GetTransactionDTO(transaction_id=5)]

    response = test_client.post("/transactions/add", json=sample_transactions)

    assert response.status_code == 409
    assert response.json()["detail"] == "Transactions with the ID 5 is already in database"

    assert mock_transactions_db_service.get_many_by_id.assert_called_once
    assert mock_transactions_db_service.add_to_db.assert_not_called
    assert mock_transactions_celery_service.add_to_celery.assert_not_called
