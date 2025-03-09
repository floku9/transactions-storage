from enum import Enum


class APIErrorMessages(str, Enum):
    CELERY_IS_BUSY = "Celery still processing tasks, wait for celery to finish."
    TRANSACTIONS_EXISTS = "Transactions with the ID {transaction_ids} is already in database"
    DATE_IN_WRONG_FORMAT = "Date is not in correct format, should be YYYY-MM-DD."
    CELERY_TASK_NOT_FOUND = "Task not found. It can be deleted, or just not finished yet."


class TransactionsErrorMessages(str, Enum):
    TRANSACTION_OUT_OF_DATE = "Transactions with the ID {transaction_id} has date"
    "from lower, than is already in balance history for this client."
    TRANSACTION_NOT_FOUND = "Transaction with the ID {transaction_id} not found."
