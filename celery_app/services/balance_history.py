from decimal import Decimal

from sqlalchemy.orm import Session

from celery_app.services.crud import (
    create_balance_history,
    get_last_balance,
)
from utils.exceptions import TransactionOutOfDateException


class BalanceHistoryService:
    def __init__(self, session: Session) -> None:
        self._session = session

    def update(self, transaction: dict):
        """Updates the balance history for a customer based on a transaction.

        Args:
            customer_id (int): The ID of the customer whose balance history is being updated
            transaction (dict): Transaction details containing transaction_id, transaction_dttm,
                transaction_amt and customer_id

        Raises:
            TransactionOutOfDateException: Raised when the transaction date is earlier than the
                last recorded balance date
        """
        customer_id = transaction["customer_id"]
        transaction_dttm = transaction["transaction_dttm"]
        transaction_amt = Decimal(str(transaction["transaction_amt"]))

        last_balance = get_last_balance(self._session, customer_id, True)
        if last_balance:
            if last_balance.from_dttm > transaction["transaction_dttm"]:
                raise TransactionOutOfDateException(transaction_id=transaction["transaction_id"])
            last_balance.to_dttm = transaction_dttm
            new_balance_amount = last_balance.balance + transaction_amt
            create_balance_history(self._session, customer_id, transaction_dttm, new_balance_amount)
        else:
            create_balance_history(self._session, customer_id, transaction_dttm, transaction_amt)
        self._session.flush()
