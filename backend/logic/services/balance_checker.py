from datetime import date
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.application.dto.transactions import GetBalanceHistoryDTO
from db.models import BalanceHistory


class BalanceCheckerService:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_customer_balance_on_date(
        self, customer_id: int, on_date: date
    ) -> Optional[GetBalanceHistoryDTO]:
        """
        Retrieves the balance history for a customer.
        """

        stmt = select(BalanceHistory).filter(
            BalanceHistory.customer_id == customer_id,
            func.date(BalanceHistory.from_dttm) <= on_date,
            func.date(BalanceHistory.to_dttm) > on_date,
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model:
            dto = GetBalanceHistoryDTO(
                customer_id=model.customer_id,
                date=on_date,
                balance_amt=model.balance,
            )
            return dto
        else:
            return None
