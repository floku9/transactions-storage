from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

from backend.application.dependencies import (
    get_celery_inspector_service,
    get_transactions_celery_service,
    get_transactions_db_service,
)
from backend.application.dto.transactions import AddTransactionDTO
from backend.logic.services.celery_inspector import CeleryInspectorService
from backend.logic.services.transaction import TransactionsCeleryService, TransactionsDBService
from utils.messages import ErrorMessages

transactions_router = APIRouter(prefix="/transactions", tags=["transactions"])


@transactions_router.post("/add", response_model=str)
async def add_transactions(
    transactions: list[AddTransactionDTO],
    transactions_db_service: Annotated[TransactionsDBService, Depends(get_transactions_db_service)],
    transactions_celery_service: Annotated[
        TransactionsCeleryService, Depends(get_transactions_celery_service)
    ],
    celery_inspector_service: Annotated[
        CeleryInspectorService, Depends(get_celery_inspector_service)
    ],
):
    """
    Adds transactions to the database and asynchronously adds them to Celery.
    """
    # Check if celery has no not processed tasks
    not_finished_tasks_count = celery_inspector_service.not_finished_tasks_count()
    if not_finished_tasks_count > 0:
        raise HTTPException(status_code=429, detail=ErrorMessages.CELERY_IS_BUSY)

    already_created_transactions = await transactions_db_service.get_many_by_id(
        [tr.transaction_id for tr in transactions]
    )
    if already_created_transactions:
        # Maybe there in case of production usage we need to drop this transactions
        # from choosing and continue, but now just HTTPException
        raise HTTPException(
            status_code=409,
            detail=ErrorMessages.TRANSACTIONS_EXISTS.format(
                transaction_ids=", ".join(
                    [str(tr.transaction_id) for tr in already_created_transactions]
                )
            ),
        )

    await transactions_db_service.add_to_db(transactions)
    task_id = transactions_celery_service.add_to_celery(transactions)
    return JSONResponse(status_code=202, content=task_id)
