from datetime import datetime
from typing import Annotated

from pydantic import Field

from backend.application.dto.base import BaseDTO


class AddTransactionDTO(BaseDTO):
    transaction_id: Annotated[int, Field(ge=0, example=1)]
    transaction_dttm: Annotated[
        datetime, Field(example="2022-01-01 12:00:00", ge=datetime(1970, 1, 1))
    ]
    customer_id: Annotated[int, Field(ge=0, example=1)]
    transaction_amt: float
