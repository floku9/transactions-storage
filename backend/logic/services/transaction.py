from sqlalchemy.ext.asyncio import AsyncSession

from backend.application.dto.transactions import AddTransactionDTO
from celery import Celery
from db.models import Transaction
from settings import celery_settings
from utils.logging import logger


class TransactionsService:
    def __init__(self, db_session: AsyncSession, celery_client: Celery):
        self._db_session = db_session
        self._celery_client = celery_client

    async def add_to_db(self, transactions: list[AddTransactionDTO]) -> None:
        """
        Adds a list of transactions to the database asynchronously.

        Args:
            transactions (list[AddTransactionDTO]): A list of transaction DTOs to be
                added to the database.

        Returns:
            None: This function does not return a value.
        """
        async with self._db_session.begin():
            transaction_models: list[Transaction] = []
            for transaction_dto in transactions:
                model = Transaction(**transaction_dto.model_dump())
                transaction_models.append(model)

            self._db_session.add_all(transaction_models)
            await self._db_session.flush()
            await self._db_session.commit()
        logger.info("Successfully added transactions to database")

    def add_to_celery(self, transactions: list[AddTransactionDTO]) -> str:
        """
        Sends a list of transactions to a Celery task queue for asynchronous processing.

        Args:
            transactions (list[AddTransactionDTO]): A list of transaction DTOs to be processed.

        Returns:
            celery_id (str): The ID of the Celery task that was created for
                processing the transactions.
        """
        task = self._celery_client.send_task(
            celery_settings.CELERY_PROCESS_TRANSACTIONS_TASK_NAME,
            args=[tr.model_dump() for tr in transactions],
            queue=celery_settings.CELERY_QUEUE_NAME,
        )
        return task.id
