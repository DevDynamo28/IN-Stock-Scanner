# rs_outperformance_kite_system/output/telegram_bot.py

import requests
import yaml


def load_secrets(path='config/secrets.yaml'):
    with open(path, 'r') as f:
        return yaml.safe_load(f)


def send_telegram_message(message):
    secrets = load_secrets()
    token = secrets['telegram_bot_token']
    chat_id = secrets['telegram_chat_id']

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}

    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            print("[SUCCESS] Telegram alert sent.")
        else:
            print(f"[ERROR] Telegram failed: {response.text}")
    except Exception as e:
        print(f"[ERROR] Telegram exception: {e}")


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
            print(f"[SUCCESS] Sent file: {file_path}")
        else:
            print(f"[ERROR] Failed to send file: {response.text}")
    except Exception as e:
        print(f"[ERROR] Exception in sending file: {e}")
