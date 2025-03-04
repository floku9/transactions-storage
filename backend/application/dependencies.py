from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.logic.services.celery_inspector import CeleryInspectorService
from backend.logic.services.transaction import TransactionsService
from celery import Celery
from db.setup import async_session_factory
from settings import celery_settings, redis_settings


async def get_db_session():
    async with async_session_factory() as session:
        yield session


def get_celery_client():
    return Celery(
        celery_settings.CELERY_APP_NAME,
        broker=redis_settings.REDIS_URL,
        backend=redis_settings.REDIS_URL,
    )


def get_transactions_service(
    celery_client: Annotated[Celery, Depends(get_celery_client)],
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
):
    return TransactionsService(celery_client=celery_client, db_session=db_session)


def get_celery_inspector_service(
    celery_client: Annotated[Celery, Depends(get_celery_client)],
):
    return CeleryInspectorService(celery_client=celery_client)
