import time
from account.paper_account import PaperAccount


class ZerodhaBroker:
    """Broker interface supporting live and paper modes."""

    def __init__(self, mode="paper"):
        self.mode = mode
        self.account = PaperAccount() if mode == "paper" else None
        # TODO: Add real KiteConnect client for live trading

    def place_order(self, symbol, qty, price, side):
        if self.mode == "paper":
            return self.account.place_order(symbol, qty, price, side)
        raise NotImplementedError("Live trading not implemented")

    def deposit(self, amount):
        if self.mode == "paper":
            self.account.deposit(amount)
        else:
            raise NotImplementedError

    def withdraw(self, amount):
        if self.mode == "paper":
            self.account.withdraw(amount)
        else:
            raise NotImplementedError

    def get_portfolio(self):
        if self.mode == "paper":
            return self.account.get_portfolio()
        raise NotImplementedError


class DummyWebSocket:
    """Stream fake ticks for testing UI without network."""

    def __init__(self, symbols):
        self.symbols = symbols
        self.running = False

    def start(self, callback, interval=1):
        self.running = True
        while self.running:
            tick = {s: time.time() for s in self.symbols}
            callback(tick)
            time.sleep(interval)

    def stop(self):
        self.running = False
