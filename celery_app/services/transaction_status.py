from sqlalchemy.orm import Session

from celery_app.services.crud import (
    get_transaction_sync_status,
)
from db.models import TransactionStatus
from utils.exceptions import TransactionNotFoundException


class TransactionSyncStatusService:
    def __init__(self, session: Session) -> None:
        self._session = session

    def update(
        self, transaction_id: int | str, status: TransactionStatus, comment: str = None
    ) -> None:
        """Update transaction sync status.

        Args:
            transaction_id (int | str): ID of the transaction to update
            status (TransactionStatus): New status to set for the transaction
            comment (str, optional): Optional comment to add. Defaults to None.

        Raises:
            TransactionNotFoundException: If transaction with given ID is not found
        """
        transaction_sync_status = get_transaction_sync_status(self._session, transaction_id)
        if not transaction_sync_status:
            raise TransactionNotFoundException(transaction_id=transaction_id)
        transaction_sync_status.status = status
        transaction_sync_status.comment = comment
        self._session.flush()
