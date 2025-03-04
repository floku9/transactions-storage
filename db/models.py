from datetime import datetime
from enum import StrEnum

from sqlalchemy import DECIMAL, DateTime, Enum, Index, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class TransactionStatus(StrEnum):
    NOT_SYNCHRONIZED = "not_synchronized"
    SYNCHRONIZED = "synchronized"


class Base(DeclarativeBase): ...


class Transaction(Base):
    __tablename__ = "transactions"
    transaction_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    transaction_dttm: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    transaction_amt: Mapped[float] = mapped_column(DECIMAL(precision=12, scale=2), nullable=False)
    customer_id: Mapped[int] = mapped_column(nullable=False)
    status: Mapped[TransactionStatus] = mapped_column(
        Enum(TransactionStatus, name="transaction_status"),
        nullable=False,
        default=TransactionStatus.NOT_SYNCHRONIZED,
    )


class BalanceHistory(Base):
    __tablename__ = "balance_history"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    customer_id: Mapped[int] = mapped_column(nullable=False)
    from_dttm: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    to_dttm: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    balance: Mapped[float] = mapped_column(DECIMAL(precision=12, scale=2), nullable=False)

    __table_args__ = (
        UniqueConstraint("customer_id", "from_dttm", name="uq_customer_from"),
        Index("idx_customer_from", "customer_id", "from_dttm"),
    )
