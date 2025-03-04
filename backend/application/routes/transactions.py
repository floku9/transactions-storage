from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

from backend.application.dependencies import get_celery_inspector_service, get_transactions_service
from backend.application.dto.transactions import AddTransactionDTO
from backend.logic.services.celery_inspector import CeleryInspectorService
from backend.logic.services.transaction import TransactionsService
from utils.messages import ErrorMessages

transactions_router = APIRouter(prefix="/transactions", tags=["transactions"])


@transactions_router.post("/add", response_model=str)
async def add_transactions(
    transactions: list[AddTransactionDTO],
    transactions_service: Annotated[TransactionsService, Depends(get_transactions_service)],
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

    await transactions_service.add_to_db(transactions)
    task_id = transactions_service.add_to_celery(transactions)
    return JSONResponse(status_code=202, content=task_id)
