from datetime import datetime
from typing import List

import pytest
import redis

from backend.application.dto.transactions import AddTransactionDTO
from backend.logic.services.balance_checker import BalanceCheckerService
from backend.logic.services.redis_queue import RedisQueueService
from backend.logic.services.transaction import TransactionsCeleryService, TransactionsDBService

test_db_url = "sqlite+aiosqlite:///:memory:"


@pytest.fixture
def test_transaction_dto() -> List[AddTransactionDTO]:
    return [
        AddTransactionDTO(
            transaction_id=3,
            transaction_dttm=datetime(2025, 1, 1),
            customer_id=1,
            transaction_amt=100.0,
        ),
    ]


@pytest.fixture
def test_transactions_db_service(test_db_session):
    return TransactionsDBService(db_session=test_db_session)


@pytest.fixture
def test_transactions_celery_service(mock_celery):
    return TransactionsCeleryService(celery=mock_celery)


@pytest.fixture
def test_balance_checker_service(test_db_session):
    return BalanceCheckerService(session=test_db_session)


@pytest.fixture
def test_redis_queue_service(test_redis_client):
    return RedisQueueService(test_redis_client)
