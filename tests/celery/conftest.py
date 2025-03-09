from datetime import datetime

import pytest
from mock import MagicMock, patch
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from db.models import BalanceHistory, Base, Transaction, TransactionStatus, TransactionSyncStatus

sync_test_db_url = "sqlite:///:memory:"


@pytest.fixture(scope="session")
def sync_test_db_engine():
    engine = create_engine(sync_test_db_url, echo=False)
    yield engine
    engine.dispose()


@pytest.fixture(scope="session")
def sync_create_tables(sync_test_db_engine):
    Base.metadata.create_all(bind=sync_test_db_engine)
    yield
    Base.metadata.drop_all(bind=sync_test_db_engine)


@pytest.fixture(scope="session")
def sync_session_factory(sync_test_db_engine, sync_create_tables):
    return sessionmaker(
        bind=sync_test_db_engine,
        class_=Session,
        autocommit=False,
        autoflush=False,
    )


@pytest.fixture(scope="session")
def sync_populate_test_db(sync_session_factory):
    with sync_session_factory() as session:
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
            to_dttm=datetime(9999, 1, 1, 0, 0, 0),
            balance=300.0,
        )
        sync_status1 = TransactionSyncStatus(
            transaction_id=1,
            status=TransactionStatus.NOT_SYNCHRONIZED,
            comment="Initial for transaction 1",
        )
        sync_status2 = TransactionSyncStatus(
            transaction_id=2,
            status=TransactionStatus.NOT_SYNCHRONIZED,
            comment="Initial for transaction 2",
        )
        session.add_all([transaction1, transaction2, balance_history, sync_status1, sync_status2])
        session.commit()


@pytest.fixture(scope="function")
def sync_session(sync_session_factory, sync_populate_test_db):
    session = sync_session_factory()
    yield session
    session.rollback()
    session.close()


@pytest.fixture(scope="function")
def mock_session_factory(sync_session):
    """Fixture to mock sync_session_factory and return the test session."""
    with patch("celery_app.tasks.sync_session_factory") as mock_factory:
        mock_factory.return_value = sync_session
        yield mock_factory
