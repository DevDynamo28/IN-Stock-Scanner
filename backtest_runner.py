# rs_outperformance_kite_system/backtest_runner.py

import pandas as pd
from datetime import datetime, timedelta
from strategy.rs_entry_engine import run_daily_entry_engine
from data.live_fetch.kite_client import ZerodhaKiteClient
import yaml

from tools.secrets import load_secrets

# Load config
secrets = load_secrets()

with open("config/params.yaml") as f:
    params = yaml.safe_load(f)

api_key = secrets['kite_api_key']
api_secret = secrets['kite_api_secret']
access_token = secrets['kite_access_token']

kite = ZerodhaKiteClient(api_key, api_secret, access_token)

symbols = params['stock_list']
index_symbol = params['index_symbol']

# Backtest date range
start_date = datetime(2025, 5, 1).date()
end_date = datetime(2025, 5, 15).date()
day_delta = timedelta(days=1)

results = []
current_date = start_date

while current_date <= end_date:
    print(f"[📅] Backtesting {current_date}")

    try:
        # Fetch OHLCV for each stock for last 60 days only
        stock_data = {}
        lookback_start = current_date - timedelta(days=75)  # buffer for holidays
        skipped = 0
        for symbol in symbols:
            df = kite.fetch_historical_ohlc(symbol, lookback_start, current_date)
            if not df.empty:
                stock_data[symbol] = df
            else:
                skipped += 1

        index_df = kite.fetch_historical_ohlc(index_symbol, lookback_start, current_date)

        print(f"[INFO] {len(stock_data)} symbols with data, {skipped} skipped.")

        if index_df.empty or len(stock_data) < 10:
            print(f"[SKIP] Not enough data to evaluate on {current_date}.")
            current_date += day_delta
            continue

        entries = run_daily_entry_engine(api_key, api_secret, access_token,
                                         stock_data_dict=stock_data, index_df=index_df, top_n=50)

        if not entries.empty:
            entries['date'] = current_date
            results.append(entries)

    except Exception as e:
        print(f"[ERROR] Failed on {current_date}: {e}")

    current_date += day_delta

# Save combined trades to CSV
if results:
    all_trades = pd.concat(results, ignore_index=True)
    all_trades.to_csv("output/backtest_trades.csv", index=False)
    print("[✅] Backtest complete. Results saved to output/backtest_trades.csv")
else:
    print("[📭] No trades generated in the backtest range.")
