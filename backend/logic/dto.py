from typing import Optional

from backend.application.dto.base import BaseDTO


class GetCustomerDTO(BaseDTO):
    id: int
    first_name: str
    last_name: Optional[str]


class TaskInfoDTO(BaseDTO):
    status: str
    result: Optional[str] = None
    traceback: Optional[str] = None
    date_done: Optional[str] = None
