# rs_outperformance_kite_system/strategy/rs_entry_engine.py

from core.screener import screen_stocks
import pandas as pd

def run_daily_entry_engine(api_key, api_secret, access_token, stock_data_dict, index_df, top_n=50):
    print(f"[INFO] Fetched {len(stock_data_dict)} symbols.")

    if index_df.empty or 'close' not in index_df.columns:
        print("[❌] Index data is missing or invalid.")
        return pd.DataFrame()

    print("[INFO] Running RS Screener...")
    results_df = screen_stocks(stock_data_dict, index_df, top_n=top_n)

    return results_df