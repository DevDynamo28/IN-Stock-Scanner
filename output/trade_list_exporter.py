# rs_outperformance_kite_system/output/trade_list_exporter.py

import pandas as pd
import os
from datetime import datetime
from output.telegram_bot import send_telegram_message
import requests
import yaml


def load_secrets(path='config/secrets.yaml'):
    with open(path, 'r') as f:
        return yaml.safe_load(f)


def save_trade_report(df,
                      report_name="RS_Trade_List",
                      filetype="csv",
                      send_telegram=False):
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"{report_name}_{date_str}.{filetype}"
    output_path = os.path.join("output", "reports", filename)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    if filetype == "csv":
        df.to_csv(output_path, index=False)
    elif filetype == "xlsx":
        df.to_excel(output_path, index=False, engine='openpyxl')

    print(f"[SUCCESS] Report saved: {output_path}")

    if send_telegram:
        send_file_to_telegram(output_path)


def send_file_to_telegram(file_path):
    secrets = load_secrets()
    token = secrets['telegram_bot_token']
    chat_id = secrets['telegram_chat_id']

    url = f"https://api.telegram.org/bot{token}/sendDocument"
    try:
        with open(file_path, 'rb') as file:
            response = requests.post(url,
                                     data={'chat_id': chat_id},
                                     files={'document': file})
        if response.status_code == 200:
            print("[SUCCESS] Report sent to Telegram.")
        else:
            print(f"[ERROR] File send failed: {response.text}")
    except Exception as e:
        print(f"[ERROR] Exception in sending file: {e}")
