import pytest
from mock import Mock, patch
from sqlalchemy import select

from backend.application.dto.transactions import AddTransactionDTO
from backend.logic.services.transaction import TransactionsService
from db.models import Transaction
from settings import celery_settings


@pytest.mark.asyncio()
async def test_transactions_service_add_to_db_successfully(
    test_transactions_service: TransactionsService, test_transaction_dto: list[AddTransactionDTO]
):
    await test_transactions_service.add_to_db(test_transaction_dto)

    # Get from db transactions and check if they are there
    db_session = test_transactions_service._db_session
    stmt = select(Transaction).where(Transaction.transaction_id == 3)
    transaction = await db_session.scalar(stmt)

    assert transaction is not None
    assert transaction.transaction_id == 3
    assert transaction.customer_id == 1
    assert transaction.transaction_amt == 100.0


def test_add_to_celery(
    test_transactions_service: TransactionsService, test_transaction_dto: list[AddTransactionDTO]
):

    # Мок для send_task
    mock_task_id = "mock-task-id-123"
    with patch.object(
        test_transactions_service._celery_client, "send_task", return_value=Mock(id=mock_task_id)
    ) as mock_send_task:
        # Выполнение метода
        result = test_transactions_service.add_to_celery(test_transaction_dto)

        # Проверка вызова send_task с правильными аргументами
        mock_send_task.assert_called_once_with(
            celery_settings.CELERY_PROCESS_TRANSACTIONS_TASK_NAME,  # Замените на ваше имя задачи из настроек
            args=[i.model_dump() for i in test_transaction_dto],
            queue=celery_settings.CELERY_QUEUE_NAME,  # Замените на вашу очередь из настроек
        )

        # Проверка возвращаемого значения
        assert result == mock_task_id
