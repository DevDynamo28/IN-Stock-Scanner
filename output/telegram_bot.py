# rs_outperformance_kite_system/output/telegram_bot.py

import requests

from tools.secrets import load_secrets


def send_telegram_message(message):
    secrets = load_secrets()
    token = secrets['telegram_bot_token']
    chat_ids = secrets['telegram_chat_id']
    if isinstance(chat_ids, str):
        chat_ids = [chat_ids]  # support single string or list

    for chat_id in chat_ids:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
        try:
            response = requests.post(url, data=payload)
            if response.status_code == 200:
                print(f"[SUCCESS] Telegram alert sent to {chat_id}.")
            else:
                print(f"[ERROR] Telegram failed for {chat_id}: {response.text}")
        except Exception as e:
            print(f"[ERROR] Telegram exception for {chat_id}: {e}")


def send_file_to_telegram(file_path):
    secrets = load_secrets()
    token = secrets['telegram_bot_token']
    chat_ids = secrets['telegram_chat_id']
    if isinstance(chat_ids, str):
        chat_ids = [chat_ids]  # support single string or list

    url = f"https://api.telegram.org/bot{token}/sendDocument"

    for chat_id in chat_ids:
        try:
            with open(file_path, 'rb') as file:
                response = requests.post(url,
                                         data={'chat_id': chat_id},
                                         files={'document': file})
            if response.status_code == 200:
                print(f"[SUCCESS] Sent file to {chat_id}: {file_path}")
            else:
                print(f"[ERROR] Failed to send file to {chat_id}: {response.text}")
        except Exception as e:
            print(f"[ERROR] Exception sending file to {chat_id}: {e}")
