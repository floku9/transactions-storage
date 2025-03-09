from datetime import datetime

import pytest

from backend.application.dto.transactions import GetBalanceHistoryDTO


@pytest.mark.asyncio
async def test_get_customer_balance_on_date_found(test_balance_checker_service):
    customer_id = 1
    on_date = datetime(2022, 1, 1).date()

    result = await test_balance_checker_service.get_customer_balance_on_date(customer_id, on_date)

    assert result is not None
    assert isinstance(result, GetBalanceHistoryDTO)
    assert result.customer_id == customer_id
    assert result.date == on_date
    assert result.balance_amt == 300.0


@pytest.mark.asyncio
async def test_get_customer_balance_on_date_not_found(test_balance_checker_service):
    customer_id = 1
    on_date = datetime(2023, 1, 1).date()

    result = await test_balance_checker_service.get_customer_balance_on_date(customer_id, on_date)

    assert result is None


@pytest.mark.asyncio
async def test_get_customer_balance_on_date_invalid_customer(test_balance_checker_service):
    customer_id = 999  # Non-existing customer
    on_date = datetime(2022, 1, 1).date()

    result = await test_balance_checker_service.get_customer_balance_on_date(customer_id, on_date)

    assert result is None
