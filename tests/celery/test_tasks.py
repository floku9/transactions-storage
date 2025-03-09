from datetime import datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from celery_app.tasks import add_transactions_batch
from db.models import BalanceHistory, TransactionStatus, TransactionSyncStatus


def test_add_transactions_batch_success(sync_session, mock_session_factory):
    transactions = [
        {
            "transaction_id": 1,
            "customer_id": 1,
            "transaction_dttm": datetime(2022, 1, 3, 12, 0, 0),
            "transaction_amt": "150.0",
        },
        {
            "transaction_id": 2,
            "customer_id": 1,
            "transaction_dttm": datetime(2022, 1, 3, 13, 0, 0),
            "transaction_amt": "200.0",
        },
    ]

    add_transactions_batch(transactions)

    sync_status = sync_session.query(TransactionSyncStatus).filter_by(transaction_id=1).first()
    balance = (
        sync_session.query(BalanceHistory)
        .filter_by(customer_id=1)
        .order_by(BalanceHistory.from_dttm.desc())
        .first()
    )

    assert sync_status is not None
    assert sync_status.status == TransactionStatus.SYNCHRONIZED
    assert balance is not None
    assert balance.balance == Decimal("650.0")


def test_add_transactions_batch_error(sync_session: Session, mock_session_factory):
    transactions = [
        {
            "transaction_id": 2,
            "customer_id": 1,
            "transaction_dttm": datetime(2021, 1, 3, 12, 0, 0),
            "transaction_amt": "150.0",
        }
    ]

    sync_status = TransactionSyncStatus(
        transaction_id=999, status=TransactionStatus.NOT_SYNCHRONIZED
    )
    sync_session.add(sync_status)
    sync_session.commit()

    add_transactions_batch(transactions)

    sync_status = sync_session.query(TransactionSyncStatus).filter_by(transaction_id=2).first()
    assert sync_status is not None
    assert sync_status.status == TransactionStatus.ERROR
