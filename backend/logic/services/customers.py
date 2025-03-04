# from select import select
# from typing import Optional

# from sqlalchemy.ext.asyncio import AsyncSession

# from backend.logic.dto import GetCustomerDTO
# from db.models import Customer


# class CustomersService:
#     def __init__(self, db_session: AsyncSession):
#         self.db_session = db_session

#     async def get_by_id(self, customer_id) -> Optional[GetCustomerDTO]:
#         stmt = select(Customer).where(Customer.id == customer_id)
#         result = await self.db_session.execute(stmt)
#         customer = result.scalar_one_or_none()
#         if customer:
#             return GetCustomerDTO(
#                 id=customer.id,
#                 first_name=customer.first_name,
#                 last_name=customer.last_name,
#             )
#         else:
#             return None
...
