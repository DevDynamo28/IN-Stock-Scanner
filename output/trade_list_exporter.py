# rs_outperformance_kite_system/output/trade_list_exporter.py

import pandas as pd
import os
from datetime import datetime
from output.telegram_bot import send_telegram_message
import requests

from tools.secrets import load_secrets


def save_trade_report(df,
                      report_name="RS_Trade_List",
                      filetype="csv",
                      send_telegram=False):
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"{report_name}_{date_str}.{filetype}"
    output_path = os.path.join("output", "reports", filename)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Reorder columns if they exist
    preferred_order = [
        'symbol', 'RS Alpha', 'RS Pattern', 'Close', 'AMA',
        'Fusion Score', 'Volume Confirm'
    ]
    df = df[[col for col in preferred_order if col in df.columns]]

    # Save file
    if filetype == "csv":
        df.to_csv(output_path, index=False)
    elif filetype == "xlsx":
        df.to_excel(output_path, index=False, engine='openpyxl')

    print(f"[SUCCESS] Report saved: {output_path}")

    # Export symbols with volume confirmation only
    txt_path = os.path.join("output", "watchlist", f"tv_watchlist_{date_str}.txt")
    os.makedirs(os.path.dirname(txt_path), exist_ok=True)
    if 'Volume Confirm' in df.columns:
        confirmed_df = df[df['Volume Confirm'] == True]
    else:
        confirmed_df = df
    confirmed_df['symbol'].dropna().to_csv(txt_path, index=False, header=False)
    print(f"[EXPORT] TradingView watchlist saved: {txt_path}")

    if send_telegram:
        send_file_to_telegram(output_path)
        # Chart image suppressed intentionally
        send_file_to_telegram(txt_path)


def send_file_to_telegram(file_path, chat_ids=None):
    """Send a file to one or multiple Telegram chats."""

    secrets = load_secrets()
    token = secrets['telegram_bot_token']

    if chat_ids is None:
        chat_ids = secrets['telegram_chat_id']

    if isinstance(chat_ids, str):
        chat_ids = [chat_ids]

    url = f"https://api.telegram.org/bot{token}/sendDocument"

    for chat_id in chat_ids:
        try:
            with open(file_path, 'rb') as file:
                response = requests.post(
                    url,
                    data={'chat_id': chat_id},
                    files={'document': file}
                )
            if response.status_code == 200:
                print(f"[SUCCESS] Sent file to {chat_id}: {file_path}")
            else:
                print(f"[ERROR] Failed to send file to {chat_id}: {response.text}")
        except Exception as e:
            print(f"[ERROR] Exception sending file to {chat_id}: {e}")
