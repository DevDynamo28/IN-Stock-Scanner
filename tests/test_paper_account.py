from account.paper_account import PaperAccount


def test_avg_price_and_qty_updates():
    acc = PaperAccount(starting_balance=1000)
    acc.place_order("A", 2, 100, "buy")
    acc.place_order("A", 2, 200, "buy")
    assert acc.holdings["A"]["qty"] == 4
    assert acc.holdings["A"]["avg_price"] == 150

    acc.place_order("A", 1, 180, "sell")
    assert acc.holdings["A"]["qty"] == 3
    assert acc.balance == 580

