try:
    from kiteconnect import KiteTicker
except Exception:  # pragma: no cover - optional dependency may be missing
    KiteTicker = None
from broker.zerodha import DummyWebSocket
import time
import threading


class LivePriceStreamer:
    """Stream live prices using KiteTicker with a fallback DummyWebSocket."""

    def __init__(self, api_key, access_token, token_map):
        self.api_key = api_key
        self.access_token = access_token
        self.token_map = token_map
        self.ticker = None
        self.dummy = None

    def _parse_ticks(self, ticks):
        data = {}
        for t in ticks:
            token = t.get("instrument_token")
            price = t.get("last_price")
            for sym, tok in self.token_map.items():
                if tok == token:
                    data[sym] = price
        return data

    def start(self, symbols, callback):
        tokens = [self.token_map.get(s) for s in symbols if s in self.token_map]
        tokens = [t for t in tokens if t]
        if KiteTicker is None:
            print("[WARN] KiteTicker unavailable. Using DummyWebSocket.")
            self.dummy = DummyWebSocket(symbols)
            self.dummy.start(callback)
            return
        try:
            self.ticker = KiteTicker(self.api_key, self.access_token)

            def on_ticks(ws, ticks):
                data = self._parse_ticks(ticks)
                if data:
                    callback(data)

            def on_connect(ws, resp):
                if tokens:
                    ws.subscribe(tokens)

            self.ticker.on_ticks = on_ticks
            self.ticker.on_connect = on_connect
            self.ticker.connect(threaded=True)
        except Exception as e:
            print(f"[WARN] Live websocket failed: {e}. Using DummyWebSocket.")
            self.dummy = DummyWebSocket(symbols)
            self.dummy.start(callback)

    def stop(self):
        if self.ticker:
            try:
                self.ticker.close()
            except Exception:
                pass
        if self.dummy:
            self.dummy.stop()

    def snapshot(self, symbols, timeout=2):
        """Return a snapshot of prices for ``symbols`` collected over ``timeout`` seconds."""
        prices = {}

        def _collect(data):
            prices.update(data)

        thread = threading.Thread(target=self.start, args=(symbols, _collect))
        thread.daemon = True
        thread.start()
        time.sleep(timeout)
        self.stop()
        thread.join(timeout=0.1)
        return prices
