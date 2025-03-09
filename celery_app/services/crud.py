from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from db.models import BalanceHistory, Transaction, TransactionSyncStatus


def get_transaction_by_id(
    session: Session, transaction_id: int, lock: bool = False
) -> Optional[Transaction]:
    """
    Retrieve a transaction by its ID from the database.

    Args:
        session (Session): SQLAlchemy database session
        transaction_id (int): ID of the transaction to retrieve
        lock (bool, optional): Whether to lock the row for update. Defaults to False.

    Returns:
        Optional[Transaction]: Transaction object if found, None otherwise
    """
    stmt = select(Transaction).where(Transaction.transaction_id == transaction_id)
    if lock:
        stmt = stmt.with_for_update()
    result = session.execute(stmt)
    return result.scalar_one_or_none()


def get_last_balance(
    session: Session, customer_id: int, lock: bool = False
) -> Optional[BalanceHistory]:
    """
    Retrieve the most recent balance history entry for a customer.

    Args:
        session (Session): SQLAlchemy database session
        customer_id (int): ID of the customer
        lock (bool, optional): Whether to lock the row for update. Defaults to False.

    Returns:
        Optional[BalanceHistory]: Most recent BalanceHistory object if found, None otherwise
    """
    stmt = (
        select(BalanceHistory)
        .where(BalanceHistory.customer_id == customer_id)
        .order_by(BalanceHistory.to_dttm.desc())
        .limit(1)
    )
    if lock:
        stmt = stmt.with_for_update()
    result = session.execute(stmt)
    return result.scalar_one_or_none()


def create_balance_history(
    session: Session,
    customer_id: int,
    from_dttm: datetime,
    balance_amt: Decimal,
    lock: bool = False,
):
    """
    Create a new balance history entry for a customer.

    Args:
        session (Session): SQLAlchemy database session
        customer_id (int): ID of the customer
        from_dttm (datetime): Start date and time of the balance record
        balance_amt (Decimal): Balance amount
        lock (bool, optional): Whether to lock the row for update. Defaults to False.
    """
    balance = BalanceHistory(
        customer_id=customer_id, from_dttm=from_dttm, to_dttm=datetime.max, balance=balance_amt
    )
    session.add(balance)
    session.flush()


def get_transaction_sync_status(session: Session, transaction_id: int | str):
    """
    Retrieve the synchronization status of a transaction.

    Args:
        session (Session): SQLAlchemy database session
        transaction_id (int | str): ID of the transaction

    Returns:
        Optional[TransactionSyncStatus]: TransactionSyncStatus object if found, None otherwise
    """
    stmt = select(TransactionSyncStatus).where(
        TransactionSyncStatus.transaction_id == transaction_id
    )
    result = session.execute(stmt)
    return result.scalar_one_or_none()
