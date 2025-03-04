from datetime import datetime
from typing import List

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from backend.application.dto.transactions import AddTransactionDTO
from backend.logic.services.celery_inspector import CeleryInspectorService
from backend.logic.services.transaction import TransactionsService
from celery import Celery
from db.models import BalanceHistory, Base, Transaction

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
            from_dttm=datetime(2022, 1, 1, 0, 0, 0),
            to_dttm=datetime(2022, 1, 2, 0, 0, 0),
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


@pytest.fixture
def mock_celery():
    celery = Celery("test_app")
    celery.conf.task_always_eager = True
    return celery


@pytest.fixture
def test_transactions_service(test_db_session, mock_celery):
    return TransactionsService(db_session=test_db_session, celery_client=mock_celery)


@pytest.fixture
def test_celery_inspector_service(mock_celery):
    return CeleryInspectorService(celery_client=mock_celery)
