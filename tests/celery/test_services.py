from datetime import datetime
from decimal import Decimal

import pytest
from sqlalchemy.orm import Session

from celery_app.services.balance_history import BalanceHistoryService
from celery_app.services.transaction_status import TransactionSyncStatusService
from db.models import BalanceHistory, TransactionStatus, TransactionSyncStatus
from utils.exceptions import TransactionNotFoundException, TransactionOutOfDateException


def test_transaction_sync_status_update_success(sync_session: Session):
    service = TransactionSyncStatusService(sync_session)

    # Act
    service.update(1, TransactionStatus.SYNCHRONIZED, "Updated")

    # Assert
    updated_status = sync_session.query(TransactionSyncStatus).filter_by(transaction_id=1).first()
    assert updated_status is not None
    assert updated_status.status == TransactionStatus.SYNCHRONIZED
    assert updated_status.comment == "Updated"


def test_transaction_sync_status_update_not_found(sync_session: Session):
    service = TransactionSyncStatusService(sync_session)

    with pytest.raises(TransactionNotFoundException):
        service.update(999, TransactionStatus.SYNCHRONIZED)


# Тесты для BalanceHistoryService
def test_balance_history_update_new_transaction(sync_session: Session):
    service = BalanceHistoryService(sync_session)
    transaction = {
        "transaction_id": 3,
        "customer_id": 1,
        "transaction_dttm": datetime(2022, 1, 3, 12, 0, 0),
        "transaction_amt": "150.0",
    }

    service.update(transaction)

    balance = (
        sync_session.query(BalanceHistory)
        .filter_by(customer_id=1)
        .order_by(BalanceHistory.from_dttm.desc())
        .first()
    )
    assert balance is not None
    assert balance.balance == Decimal("450.0")  # 300 + 150
    assert balance.from_dttm == transaction["transaction_dttm"]


def test_balance_history_update_out_of_date(sync_session: Session):
    service = BalanceHistoryService(sync_session)
    transaction = {
        "transaction_id": 3,
        "customer_id": 1,
        "transaction_dttm": datetime(2021, 12, 31, 12, 0, 0),  # Раньше существующего баланса
        "transaction_amt": "150.0",
    }

    with pytest.raises(TransactionOutOfDateException):
        service.update(transaction)
