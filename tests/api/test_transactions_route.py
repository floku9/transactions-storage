from fastapi.testclient import TestClient
from mock import AsyncMock

from backend.application.dto.transactions import GetTransactionDTO
from utils.messages import ErrorMessages


def test_add_transactions_success(
    test_client: TestClient,
    mock_transactions_db_service: AsyncMock,
    mock_transactions_celery_service: AsyncMock,
    mock_celery_inspector_service: AsyncMock,
    sample_transactions: list[dict],
):
    # Arrange
    mock_celery_inspector_service.not_finished_tasks_count.return_value = 0
    mock_transactions_db_service.add_to_db.return_value = None
    mock_transactions_celery_service.add_to_celery.return_value = "task-123"
    mock_transactions_db_service.get_many_by_id.return_value = None

    # Act
    response = test_client.post("/transactions/add", json=sample_transactions)

    # Assert
    assert response.status_code == 202
    assert response.json() == "task-123"
    assert mock_celery_inspector_service.not_finished_tasks_count.assert_called_once
    assert mock_transactions_db_service.add_to_db.assert_called_once
    assert mock_transactions_celery_service.add_to_celery.assert_called_once


def test_add_transactions_celery_busy(
    test_client: TestClient,
    mock_transactions_db_service: AsyncMock,
    mock_transactions_celery_service: AsyncMock,
    mock_celery_inspector_service: AsyncMock,
    sample_transactions: list[dict],
):

    mock_celery_inspector_service.not_finished_tasks_count.return_value = 5
    # Act
    response = test_client.post("/transactions/add", json=sample_transactions)

    # Assert
    assert response.status_code == 429
    assert response.json()["detail"] == ErrorMessages.CELERY_IS_BUSY
    assert mock_celery_inspector_service.not_finished_tasks_count.assert_called_once
    assert mock_transactions_db_service.add_to_db.assert_not_called
    assert mock_transactions_celery_service.add_to_celery.assert_not_called


def test_transactions_already_in_db(
    test_client: TestClient,
    mock_transactions_db_service: AsyncMock,
    mock_transactions_celery_service: AsyncMock,
    mock_celery_inspector_service: AsyncMock,
    sample_transactions: list[dict],
):
    # Arrange
    mock_celery_inspector_service.not_finished_tasks_count.return_value = 0
    mock_transactions_db_service.get_many_by_id.return_value = [
        GetTransactionDTO(transaction_id=5)
    ]

    response = test_client.post("/transactions/add", json=sample_transactions)

    assert response.status_code == 409
    assert response.json()["detail"] == "Transactions with the ID 5 is already in database"

    assert mock_transactions_db_service.get_many_by_id.assert_called_once
    assert mock_transactions_db_service.add_to_db.assert_not_called
    assert mock_transactions_celery_service.add_to_celery.assert_not_called
