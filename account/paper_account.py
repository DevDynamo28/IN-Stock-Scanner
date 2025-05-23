class PaperAccount:
    """Simple paper trading account to simulate Zerodha features."""

    def __init__(self, starting_balance=0.0):
        self.balance = float(starting_balance)
        # holdings are stored as {symbol: {"qty": int, "avg_price": float}}
        self.holdings = {}
        self.order_history = []

    def deposit(self, amount):
        self.balance += float(amount)
        self.order_history.append({"action": "deposit", "amount": amount})

    def withdraw(self, amount):
        if amount > self.balance:
            raise ValueError("Insufficient balance")
        self.balance -= float(amount)
        self.order_history.append({"action": "withdraw", "amount": amount})

    def place_order(self, symbol, qty, price, side):
        cost = qty * price
        if side.lower() == "buy" and cost > self.balance:
            raise ValueError("Insufficient funds")
        order = {
            "symbol": symbol,
            "qty": qty,
            "price": price,
            "side": side,
        }

        current = self.holdings.get(symbol, {"qty": 0, "avg_price": 0.0})
        if side.lower() == "buy":
            self.balance -= cost
            new_qty = current["qty"] + qty
            new_avg = (
                current["avg_price"] * current["qty"] + price * qty
            ) / new_qty
            self.holdings[symbol] = {"qty": new_qty, "avg_price": new_avg}
        else:
            held_qty = current.get("qty", 0)
            if qty > held_qty:
                raise ValueError("Not enough holdings to sell")
            new_qty = held_qty - qty
            self.balance += cost
            if new_qty == 0:
                self.holdings.pop(symbol, None)
            else:
                self.holdings[symbol] = {
                    "qty": new_qty,
                    "avg_price": current["avg_price"],
                }
        self.order_history.append(order)
        return order

    def get_portfolio(self):
        return {
            "balance": self.balance,
            "holdings": dict(self.holdings),
            "orders": list(self.order_history),
        }
