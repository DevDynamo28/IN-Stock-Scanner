class PaperAccount:
    """Simple paper trading account to simulate Zerodha features."""

    def __init__(self, starting_balance=0.0):
        self.balance = float(starting_balance)
        # Store holdings as mapping of symbol -> {"qty": int, "avg_price": float}
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
        if side.lower() == "buy":
            self.balance -= cost
            pos = self.holdings.get(symbol)
            if pos:
                total_qty = pos["qty"] + qty
                avg_price = (pos["avg_price"] * pos["qty"] + price * qty) / total_qty
                pos["qty"] = total_qty
                pos["avg_price"] = avg_price
            else:
                self.holdings[symbol] = {"qty": qty, "avg_price": price}
        else:
            pos = self.holdings.get(symbol)
            held = pos["qty"] if pos else 0
            if qty > held:
                raise ValueError("Not enough holdings to sell")
            pos["qty"] -= qty
            if pos["qty"] == 0:
                del self.holdings[symbol]
            self.balance += cost
        self.order_history.append(order)
        return order

    def get_portfolio(self):
        return {
            "balance": self.balance,
            "holdings": dict(self.holdings),
            "orders": list(self.order_history),
        }
