import requests
import pandas as pd

def get_nifty500_stock_list():
    url = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%20500"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.nseindia.com/"
    }

    session = requests.Session()
    try:
        session.get("https://www.nseindia.com", headers=headers)  # set cookies
        response = session.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            constituents = data['data']
            symbols = [item['symbol'] for item in constituents]
            print(f"[✅] Retrieved {len(symbols)} stocks from Nifty 500.")
            return symbols
        else:
            print(f"[❌] Failed to fetch data. Status: {response.status_code}")
            return []
    except Exception as e:
        print(f"[❌] Exception occurred: {e}")
        return []

# Example use
nifty500_list = get_nifty500_stock_list()
for s in nifty500_list[:10]:
    print(s)
