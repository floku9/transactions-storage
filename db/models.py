from datetime import datetime
from decimal import Decimal
from enum import Enum

from sqlalchemy import DECIMAL, DateTime, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class TransactionStatus(str, Enum):
    NOT_SYNCHRONIZED = "NOT SYNCHRONIZED"
    SYNCHRONIZED = "SYNCHRONIZED"
    ERROR = "ERROR"


class Base(DeclarativeBase): ...


class Transaction(Base):
    __tablename__ = "transactions"
    transaction_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    transaction_dttm: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=False,
    )
    transaction_amt: Mapped[float] = mapped_column(DECIMAL(precision=12, scale=2), nullable=False)
    customer_id: Mapped[int] = mapped_column(nullable=False)

    sync_status: Mapped["TransactionSyncStatus"] = relationship(
        back_populates="transaction", uselist=False
    )


class BalanceHistory(Base):
    __tablename__ = "balance_history"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    customer_id: Mapped[int] = mapped_column(nullable=False)
    from_dttm: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=False,
    )
    to_dttm: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=False,
    )
    balance: Mapped[Decimal] = mapped_column(DECIMAL(precision=12, scale=2), nullable=False)

    __table_args__ = (
        UniqueConstraint("customer_id", "from_dttm", name="uq_customer_from"),
        Index("idx_customer_from", "customer_id", "from_dttm"),
    )


class TransactionSyncStatus(Base):
    __tablename__ = "transaction_sync_status"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    transaction_id: Mapped[int] = mapped_column(
        ForeignKey("transactions.transaction_id"), nullable=False
    )
    status: Mapped[TransactionStatus] = mapped_column(
        String, nullable=False, default=TransactionStatus.NOT_SYNCHRONIZED
    )
    comment: Mapped[str] = mapped_column(nullable=True)

    transaction: Mapped["Transaction"] = relationship(back_populates="sync_status")
