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

def test_avg_price_and_balance_on_buy_sell():
    acc = PaperAccount(starting_balance=1000)
    acc.place_order("A", 2, 100, "buy")   # Spends 200
    acc.place_order("A", 2, 200, "buy")   # Spends 400 → avg = (2*100 + 2*200)/4 = 150
    assert acc.holdings["A"]["qty"] == 4
    assert acc.holdings["A"]["avg_price"] == 150

    acc.place_order("A", 1, 180, "sell")  # Gains 180
    assert acc.holdings["A"]["qty"] == 3
    assert acc.balance == pytest.approx(1000 - 600 + 180)
