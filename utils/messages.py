from enum import Enum


class ErrorMessages(str, Enum):
    CELERY_IS_BUSY = "Celery still processing tasks, wait for celery to finish."
    TRANSACTIONS_EXISTS = "Transactions with the ID {transaction_ids} is already in database"
