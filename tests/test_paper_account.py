import pytest
from account.paper_account import PaperAccount


def test_avg_price_updates():
    acc = PaperAccount()
    acc.deposit(1000)
    acc.place_order("ABC", 1, 100, "buy")
    acc.place_order("ABC", 1, 200, "buy")
    holding = acc.holdings["ABC"]
    assert holding["qty"] == 2
    assert holding["avg_price"] == pytest.approx(150.0)


def test_sell_reduces_quantity():
    acc = PaperAccount()
    acc.deposit(500)
    acc.place_order("XYZ", 2, 100, "buy")
    acc.place_order("XYZ", 1, 100, "sell")
    holding = acc.holdings["XYZ"]
    assert holding["qty"] == 1
    assert holding["avg_price"] == 100
