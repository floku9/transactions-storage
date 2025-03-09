from utils.messages import TransactionsErrorMessages


class TransactionNotFoundException(Exception):
    def __init__(self, transaction_id: int | str):
        super().__init__(
            TransactionsErrorMessages.TRANSACTION_NOT_FOUND.format(transaction_id=transaction_id)
        )


class TransactionOutOfDateException(Exception):
    def __init__(self, transaction_id: int | str):
        super().__init__(
            TransactionsErrorMessages.TRANSACTION_OUT_OF_DATE.format(transaction_id=transaction_id)
        )
