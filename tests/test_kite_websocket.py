import time
from data.live_fetch.kite_websocket import LivePriceStreamer


def test_snapshot_returns_prices():
    token_map = {"AAA": 1}
    streamer = LivePriceStreamer("key", "token", token_map)
    prices = streamer.snapshot(["AAA"], timeout=0.1)
    assert "AAA" in prices
