from datetime import datetime

import pytest
import pytest_asyncio
import redis
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from backend.application.app import app
from backend.application.dependencies import (
    get_redis_queue_service,
    get_transactions_celery_service,
    get_transactions_db_service,
)
from backend.logic.services.redis_queue import RedisQueueService
from backend.logic.services.transaction import TransactionsCeleryService, TransactionsDBService
from db.models import BalanceHistory, Base, Transaction


@pytest.fixture
def mock_transactions_db_service(mocker):
    return mocker.AsyncMock(spec=TransactionsDBService)


@pytest.fixture
def mock_transactions_celery_service(mocker):
    return mocker.AsyncMock(spec=TransactionsCeleryService)


@pytest.fixture(scope="function")
def test_redis_client():
    client = redis.Redis(host="localhost", port=6379, db=15)
    try:
        client.flushdb()
        yield client
    finally:
        client.flushdb()
        client.close()


@pytest.fixture
def test_redis_queue_service(test_redis_client):
    return RedisQueueService(test_redis_client)


@pytest.fixture
def test_client(
    mock_transactions_db_service,
    mock_transactions_celery_service,
    test_redis_queue_service,
) -> TestClient:
    # Override dependencies
    app.dependency_overrides[get_transactions_db_service] = lambda: mock_transactions_db_service
    app.dependency_overrides[get_transactions_celery_service] = (
        lambda: mock_transactions_celery_service
    )
    app.dependency_overrides[get_redis_queue_service] = lambda: test_redis_queue_service
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


test_db_url = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="session")
async def test_db_engine():
    engine = create_async_engine(test_db_url, echo=False)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="session")
async def create_tables(test_db_engine):
    async with test_db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@pytest_asyncio.fixture(scope="session")
def session_factory(test_db_engine):
    return async_sessionmaker(
        bind=test_db_engine,
        class_=AsyncSession,
    )


@pytest_asyncio.fixture(scope="session")
async def populate_test_db(session_factory, create_tables):
    async with session_factory() as session:
        transaction1 = Transaction(
            transaction_id=1,
            transaction_dttm=datetime(2022, 1, 1, 12, 0, 0),
            transaction_amt=100.0,
            customer_id=1,
        )
        transaction2 = Transaction(
            transaction_id=2,
            transaction_dttm=datetime(2022, 1, 2, 12, 0, 0),
            transaction_amt=200.0,
            customer_id=1,
        )

        balance_history = BalanceHistory(
            id=1,
            customer_id=1,
            from_dttm=datetime(2022, 1, 1),
            to_dttm=datetime(2022, 1, 2),
            balance=300.0,
        )

        # Add and commit the test data
        session.add_all([transaction1, transaction2, balance_history])
        await session.commit()


@pytest_asyncio.fixture(scope="function")
async def test_db_session(session_factory, populate_test_db):
    async with session_factory() as session:
        yield session
        await session.rollback()
