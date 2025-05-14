# rs_outperformance_kite_system/main.py

from data.live_fetch.kite_client import ZerodhaKiteClient
from strategy.rs_entry_engine import run_daily_entry_engine
from output.trade_list_exporter import save_trade_report
from output.telegram_bot import send_telegram_message, send_file_to_telegram
from tools.charting import plot_rs_chart
from core.rs_calculator import add_ama, add_donchian_channel

import yaml
from datetime import datetime, timedelta

# Load config and secrets
with open("config/secrets.yaml", "r") as f:
    secrets = yaml.safe_load(f)

with open("config/params.yaml", "r") as f:
    config = yaml.safe_load(f)

# Credentials
api_key = secrets['kite_api_key']
api_secret = secrets['kite_api_secret']
access_token = secrets['kite_access_token']

# Initialize Kite
kite = ZerodhaKiteClient(api_key, api_secret, access_token)

# Load symbols from params.yaml
symbols = config.get('stock_list', [])
index_symbol = config.get('index_symbol', 'NIFTY')
top_n = config.get('top_n', 50)
print(f"[📦] Loaded {len(symbols)} symbols from config.")

# Define date range for OHLC
days_of_data = 50
holiday_buffer = 30
today = datetime.now().date()
start = today - timedelta(days=days_of_data + holiday_buffer)
end = today
print(f"[🗓️] Date range: {start} to {end}")

# Step 1: Fetch OHLCV Data
print("[INFO] Fetching stock data...")
stock_data_dict = kite.fetch_multiple_ohlc(symbols)

print("[INFO] Fetching index data...")
index_df = kite.fetch_index_data(index_symbol, start=start, end=end)

# Step 2: Run RS Screener
print("[INFO] Running RS entry screener...")
entry_df = run_daily_entry_engine(
    api_key, api_secret, access_token,
    stock_data_dict=stock_data_dict,
    index_df=index_df,
    top_n=top_n
)

# Step 3: Save Report + Charts + Telegram
if not entry_df.empty:
    save_trade_report(entry_df, report_name="RS_Trade_List", filetype="xlsx", send_telegram=True)

    for _, row in entry_df.iterrows():
        symbol = row['symbol']
        pattern = row['RS Pattern']
        alpha = row['RS Alpha']
        stock_df = stock_data_dict[symbol]

        # Ensure required indicators are available
        stock_df = add_ama(stock_df)
        stock_df = add_donchian_channel(stock_df)

        try:
            close = stock_df['close'].iloc[-1]
            ama = stock_df['ama'].iloc[-1]
            donchian_high = stock_df['donchian_high'].iloc[-1]
            swing_low = stock_df['low'].rolling(window=5).min().iloc[-1]

            target = round(donchian_high * 1.01, 2)
            stoploss = round(min(ama, swing_low), 2)

            message = (
                f"🚀 RS Entry: {symbol}\n"
                f"📊 Pattern: {pattern}\n"
                f"📈 Alpha: {alpha:.4f}\n\n"
                f"✅ Decision: ENTRY CANDIDATE\n\n"
                f"🎯 Target: ₹{target} (Donchian High + buffer)\n"
                f"🛡️ Stoploss: ₹{stoploss} (Below AMA or last swing low)"
            )
        except Exception as e:
            print(f"[ERROR] Message formatting failed for {symbol}: {e}")
            message = (
                f"⚠️ RS Entry: {symbol}\n"
                f"Pattern: {pattern}\n"
                f"Alpha: {alpha:.4f}"
            )

        send_telegram_message(message)

        chart_path = plot_rs_chart(symbol, stock_df, index_df, pattern=pattern)
        if chart_path:
            send_file_to_telegram(chart_path)

else:
    send_telegram_message("📭 *No RS entries found today.*")

print("[✅] RS System run complete.")