from handlers.api.bybit import BybitHandler
import pytest


@pytest.fixture
def bybit():
    return BybitHandler()


def test_get_available_budget_usdt(bybit):
    result = bybit.get_available_budget_usdt()
    print(result)
    assert isinstance(result, float)


def test_truncate(bybit):
    result = bybit.truncate(1.234567, 2)
    assert isinstance(result, float)
