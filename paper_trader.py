"""Simple paper trading script with auto entry, exit and live P&L."""

import time
from datetime import datetime, timedelta

from broker.zerodha import ZerodhaBroker
from data.live_fetch.kite_client import ZerodhaKiteClient
from data.live_fetch.kite_websocket import LivePriceStreamer
from strategy.rs_entry_engine import run_daily_entry_engine
from strategy.rs_exit_engine import evaluate_exit
from strategy.rotation_model import rotate_portfolio
from tools.watchlist import load_latest_watchlist
from tools.secrets import load_secrets


class PaperTrader:
    def __init__(self):
        self.secrets = load_secrets()
        self.kite = ZerodhaKiteClient(
            self.secrets['kite_api_key'],
            self.secrets['kite_api_secret'],
            self.secrets['kite_access_token'],
        )
        self.broker = ZerodhaBroker(mode="paper")
        self.positions = {}
        self.index_df = None
        self.token_map = self.kite.instrument_cache
        self.streamer = LivePriceStreamer(
            self.secrets['kite_api_key'],
            self.secrets['kite_access_token'],
            self.token_map,
        )

    def load_watchlist(self):
        watchlist = load_latest_watchlist()
        if watchlist:
            print(f"[INFO] Loaded {len(watchlist)} symbols from watchlist file")
            return watchlist
        print("[WARN] No watchlist found, running entry engine")
        stock_data = self.kite.fetch_multiple_ohlc(self.token_map.keys())
        self.index_df = self.kite.fetch_index_data()
        entries = run_daily_entry_engine(
            self.secrets['kite_api_key'],
            self.secrets['kite_api_secret'],
            self.secrets['kite_access_token'],
            stock_data_dict=stock_data,
            index_df=self.index_df,
        )
        return entries['symbol'].tolist()

    def enter_positions(self, symbols):
        if self.index_df is None:
            self.index_df = self.kite.fetch_index_data()
        stock_data = self.kite.fetch_multiple_ohlc(symbols)
        for sym in symbols:
            df = stock_data.get(sym)
            if df is None or df.empty:
                continue
            price = df['close'].iloc[-1]
            self.broker.place_order(sym, 1, price, 'buy')
            self.positions[sym] = {
                'entry': price,
                'data': df,
            }
            print(f"[ENTRY] {sym} @ {price}")

    def check_exits(self, prices):
        to_exit = []
        for sym, info in self.positions.items():
            df = info['data']
            price = prices.get(sym)
            if price is None:
                continue
            df.loc[datetime.now()] = price
            signal = evaluate_exit(df, self.index_df, sym)
            if signal:
                to_exit.append(sym)
        for sym in to_exit:
            price = prices[sym]
            self.broker.place_order(sym, 1, price, 'sell')
            del self.positions[sym]
            print(f"[EXIT] {sym} @ {price}")

    def print_pnl(self, prices):
        total = 0.0
        for sym, info in self.positions.items():
            price = prices.get(sym)
            if price is None:
                continue
            pnl = price - info['entry']
            total += pnl
        print(f"[P&L] {total:.2f}")

    def run(self):
        symbols = self.load_watchlist()
        if not symbols:
            print("[INFO] Nothing to trade")
            return
        self.enter_positions(symbols)

        portfolio_symbols = list(self.positions.keys())
        rotation = rotate_portfolio(
            portfolio_symbols,
            {s: self.positions[s]['data'] for s in portfolio_symbols},
            self.index_df,
            {},
            symbols,
        )
        for exit_item in rotation['exits']:
            sym = exit_item['symbol']
            price = self.positions[sym]['entry']
            self.broker.place_order(sym, 1, price, 'sell')
            del self.positions[sym]
            print(f"[ROTATE EXIT] {sym}")
        for entry_item in rotation['entries']:
            sym = entry_item['symbol']
            if sym not in self.positions:
                df = self.kite.fetch_historical_ohlc(sym, datetime.now().date() - timedelta(days=30), datetime.now().date())
                if not df.empty:
                    price = df['close'].iloc[-1]
                    self.broker.place_order(sym, 1, price, 'buy')
                    self.positions[sym] = {'entry': price, 'data': df}
                    print(f"[ROTATE ENTRY] {sym} @ {price}")

        self.streamer.start(list(self.positions.keys()), self.on_tick)

    def on_tick(self, prices):
        self.check_exits(prices)
        self.print_pnl(prices)


def main():
    trader = PaperTrader()
    try:
        trader.run()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        trader.streamer.stop()
        print("\n[STOP] Trading halted")


if __name__ == "__main__":
    main()
