from typing import Optional

from backend.application.dto.base import BaseDTO


class GetCustomerDTO(BaseDTO):
    id: int
    first_name: str
    last_name: Optional[str]
