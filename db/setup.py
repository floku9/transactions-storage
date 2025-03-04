from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, sessionmaker

from settings import db_settings

async_engine = create_async_engine(db_settings.ASYNC_DB_URL, echo=False)

async_session_factory = async_sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False, autocommit=False, autoflush=False
)


sync_engine = create_engine(
    db_settings.DB_URL,
    echo=False,
)

sync_session_factory = sessionmaker(
    sync_engine, class_=Session, expire_on_commit=False, autocommit=False, autoflush=False
)
