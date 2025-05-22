class PaperAccount:
    """Simple paper trading account to simulate Zerodha features."""

    def __init__(self, starting_balance=0.0):
        self.balance = float(starting_balance)
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
            self.holdings[symbol] = self.holdings.get(symbol, 0) + qty
        else:
            held = self.holdings.get(symbol, 0)
            if qty > held:
                raise ValueError("Not enough holdings to sell")
            self.holdings[symbol] = held - qty
            self.balance += cost
        self.order_history.append(order)
        return order

    def get_portfolio(self):
        return {
            "balance": self.balance,
            "holdings": dict(self.holdings),
            "orders": list(self.order_history),
        }
