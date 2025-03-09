from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from backend.application.dependencies import get_redis_queue_service
from backend.logic.dto import TaskInfoDTO
from backend.logic.services.redis_queue import RedisQueueService
from utils.messages import APIErrorMessages

celery_checker_router = APIRouter(prefix="/celery", tags=["celery", "info"])


@celery_checker_router.get("/task_status/{task_id}", response_model=TaskInfoDTO)
async def get_task_status(
    task_id: str,
    redis_queue_service: Annotated[RedisQueueService, Depends(get_redis_queue_service)],
) -> TaskInfoDTO:
    """Get the status of a Celery task.
    \f
    Args:
        task_id (str): The ID of the Celery task to check.
        redis_queue_service (Annotated[RedisQueueService, Depends): Service for interacting with Redis queue.

    Raises:
        HTTPException: If the task with the given ID is not found (404).

    Returns:
        TaskInfoDTO: Information about the task status including state and result.
    """
    task_status = redis_queue_service.get_task_status(task_id)
    if task_status is None:
        raise HTTPException(status_code=404, detail=APIErrorMessages.CELERY_TASK_NOT_FOUND)
    return task_status
