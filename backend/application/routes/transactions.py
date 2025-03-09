import datetime
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse

from backend.application.dependencies import (
    get_balance_checker_service,
    get_redis_queue_service,
    get_transactions_celery_service,
    get_transactions_db_service,
)
from backend.application.dto.transactions import AddTransactionDTO, GetBalanceHistoryDTO
from backend.logic.services.balance_checker import BalanceCheckerService
from backend.logic.services.redis_queue import RedisQueueService
from backend.logic.services.transaction import TransactionsCeleryService, TransactionsDBService
from settings import celery_settings
from utils.constants import DATE_REGEX
from utils.logging import logger
from utils.messages import APIErrorMessages

transactions_router = APIRouter(prefix="/transactions", tags=["transactions"])


@transactions_router.post("/add", response_model=str)
async def add_transactions(
    transactions: list[AddTransactionDTO],
    transactions_db_service: Annotated[TransactionsDBService, Depends(get_transactions_db_service)],
    transactions_celery_service: Annotated[
        TransactionsCeleryService, Depends(get_transactions_celery_service)
    ],
    redis_queue_service: Annotated[RedisQueueService, Depends(get_redis_queue_service)],
):
    """
    Add transactions to the database and process them asynchronously using Celery.
    \f
    Args:
        transactions (list[AddTransactionDTO]): List of transactions to be added and processed
        transactions_db_service (Annotated[TransactionsDBService, Depends]): Service for database
            operations with transactions
        transactions_celery_service (Annotated[TransactionsCeleryService, Depends]): Service for
            Celery task operations
        redis_queue_service (Annotated[RedisQueueService, Depends]): Service for Redis queue
            operations

    Raises:
        HTTPException: If Celery is busy processing other tasks (status code 429)
        HTTPException: If transactions with provided IDs already exist (status code 409)

    Returns:
        JSONResponse: Task ID for the created Celery task with status code 202
    """  # Check if celery has no not processed tasks
    not_finished_tasks_count = redis_queue_service.get_not_finished_tasks(
        queue_name=celery_settings.CELERY_QUEUE_NAME
    )
    if not_finished_tasks_count > 0:
        raise HTTPException(status_code=429, detail=APIErrorMessages.CELERY_IS_BUSY)

    already_created_transactions = await transactions_db_service.get_many_by_id(
        [tr.transaction_id for tr in transactions]
    )
    if already_created_transactions:
        # Maybe there in case of production usage we need to drop this transactions
        # from choosing and continue, but now just HTTPException
        raise HTTPException(
            status_code=409,
            detail=APIErrorMessages.TRANSACTIONS_EXISTS.format(
                transaction_ids=", ".join(
                    [str(tr.transaction_id) for tr in already_created_transactions]
                )
            ),
        )

    await transactions_db_service.add_to_db(transactions)
    task_id = transactions_celery_service.add_to_celery(transactions)
    return JSONResponse(status_code=202, content=task_id)


@transactions_router.get("/balance", response_model=List[GetBalanceHistoryDTO])
async def get_balance(
    date: Annotated[str, Query(..., pattern=DATE_REGEX, description="Date in format YYYY-MM-DD")],
    customer_id: Annotated[List[int], Query(..., description="Clients id list")],
    balance_checker_service: Annotated[BalanceCheckerService, Depends(get_balance_checker_service)],
):
    """
    Retrieves the balance history for the specified customers on the given date.
    \f
    Args:
        date (str): The date to retrieve the balance history for, in the format "YYYY-MM-DD".
        customer_id (List[int]): A list of customer IDs to retrieve the balance history for.
        balance_checker_service (BalanceCheckerService): The service responsible for checking the
            customer balance.

    Returns:
        List[GetBalanceHistoryDTO]: A list of balance history objects for the specified customers
            on the given date.

    Raises:
        HTTPException: If the date is in the wrong format.
        try:
        parsed_date = datetime.date.fromisoformat(date)
    except ValueError:
        raise HTTPException(status_code=400, detail=APIErrorMessages.DATE_IN_WRONG_FORMAT)
    """
    try:
        parsed_date = datetime.date.fromisoformat(date)
    except ValueError:
        raise HTTPException(status_code=400, detail=APIErrorMessages.DATE_IN_WRONG_FORMAT)

    response_list: list[GetBalanceHistoryDTO] = []
    for idx in customer_id:
        balance_history = await balance_checker_service.get_customer_balance_on_date(
            idx, parsed_date
        )
        if balance_history:
            response_list.append(balance_history)
        else:
            logger.warning(f"No balance history for customer {idx} on {date} date")

    return response_list
