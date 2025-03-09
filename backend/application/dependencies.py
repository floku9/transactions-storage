from typing import Annotated

import redis
from celery import Celery
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.logic.services.balance_checker import BalanceCheckerService
from backend.logic.services.redis_queue import RedisQueueService
from backend.logic.services.transaction import TransactionsCeleryService, TransactionsDBService
from db.setup import async_session_factory
from settings import celery_settings, redis_settings


async def get_db_session():
    async with async_session_factory() as session:
        yield session


def get_celery_client():
    return Celery(
        celery_settings.CELERY_APP_NAME,
        broker=redis_settings.REDIS_URL,
        result_backend=redis_settings.REDIS_URL,
    )


def get_redis_client() -> redis.Redis:
    return redis.from_url(redis_settings.REDIS_URL, decode_responses=True)


def get_transactions_db_service(
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
):
    return TransactionsDBService(db_session=db_session)


def get_transactions_celery_service(celery_client: Annotated[Celery, Depends(get_celery_client)]):
    return TransactionsCeleryService(celery=celery_client)


def get_balance_checker_service(
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
):
    return BalanceCheckerService(session=db_session)


def get_redis_queue_service(redis_client: Annotated[redis.Redis, Depends(get_redis_client)]):
    return RedisQueueService(redis_client=redis_client)
