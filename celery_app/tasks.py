from celery_app.config import app
from celery_app.services.balance_history import BalanceHistoryService
from celery_app.services.transaction_status import TransactionSyncStatusService
from db.models import TransactionStatus
from db.setup import sync_session_factory
from settings import celery_settings
from utils.exceptions import TransactionNotFoundException
from utils.logging import logger


@app.task(name=celery_settings.CELERY_PROCESS_TRANSACTIONS_TASK_NAME)
def add_transactions_batch(transactions: list[dict]) -> None:
    """
    Process a batch of transactions by updating their sync status and balance history.

    Args:
        transactions (list[dict]): List of transaction dictionaries containing transaction_id,
            transaction_dttm and other transaction details.

    Returns:
        None
    """
    with sync_session_factory() as session:
        balance_history_service = BalanceHistoryService(session=session)
        transaction_sync_service = TransactionSyncStatusService(session=session)
        transactions.sort(key=lambda x: x["transaction_dttm"])
        for transaction in transactions:
            try:
                with session.begin():
                    transaction_sync_service.update(
                        transaction["transaction_id"], TransactionStatus.SYNCHRONIZED
                    )
                    balance_history_service.update(transaction=transaction)

            except TransactionNotFoundException as e:
                logger.error(e)

            except Exception as e:
                logger.error(e)
                transaction_sync_service.update(
                    transaction["transaction_id"],
                    TransactionStatus.ERROR,
                    str(e),
                )
                session.commit()
