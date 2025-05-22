# rs_outperformance_kite_system/data/live_fetch/kite_client.py

from kiteconnect import KiteConnect
import pandas as pd
from datetime import datetime, timedelta, date
import time

class ZerodhaKiteClient:
    def __init__(self, api_key, api_secret, access_token):
        self.api_key = api_key
        self.api_secret = api_secret
        self.access_token = access_token
        self.kite = KiteConnect(api_key=self.api_key)
        self.kite.set_access_token(self.access_token)
        self.instrument_cache = self.build_token_cache()
        

    def build_token_cache(self):
        print("[INFO] Building instrument token cache...")
        try:
            instruments = self.kite.instruments()
        except Exception as e:
            print(f"[WARN] Failed to fetch instruments: {e}")
            return {}

        # 👉 Add this to see what index names are available
        print("[DEBUG] Sampling index instruments:")
        for item in instruments:
            if item['instrument_type'] == 'Index':
                print(f"{item['tradingsymbol']} | {item['name']} → {item['instrument_token']}")

        token_map = {}
        for item in instruments:
            if item['instrument_type'] in ['EQ', 'Index'] and item['exchange'] in ['NSE', 'NFO']:
                token_map[item['tradingsymbol']] = item['instrument_token']
        print(f"[✅] Cached {len(token_map)} tradable tokens.")
        return token_map
        
                
    def fetch_instrument_token(self, symbol):
        symbol = symbol.upper()

        # Step 1: Try from cached map
        token = self.instrument_cache.get(symbol)
        if token:
            return token

        # Step 2: Known index aliases → proper names (used by Kite)
        index_aliases = {
            "NIFTY": "NIFTY 50",
            "BANKNIFTY": "NIFTY BANK",
            "FINNIFTY": "NIFTY FINANCIAL SERVICES",
            "MIDCPNIFTY": "NIFTY MIDCAP SELECT",
            "NIFTYMIDCAP100": "NIFTY MIDCAP 100",
            "NIFTYSMALLCAP100": "NIFTY SMALLCAP 100",
            "NIFTYIT": "NIFTY IT",
            "NIFTYMETAL": "NIFTY METAL",
            "NIFTYPHARMA": "NIFTY PHARMA",
            "NIFTYAUTO": "NIFTY AUTO",
            "NIFTYFMCG": "NIFTY FMCG"
        }

        mapped_name = index_aliases.get(symbol, symbol)

        # Step 3: Try to resolve from full instrument list
        try:
            for item in self.kite.instruments():
                if item.get('name', '').upper() == mapped_name.upper() and item.get('instrument_type', '').upper() == 'INDEX':
                    token = item['instrument_token']
                    self.instrument_cache[symbol] = token
                    print(f"[DYNAMIC ✅] Resolved index token for '{symbol}' → {token}")
                    return token
        except Exception as e:
            print(f"[ERROR] Failed to resolve token from instruments for {symbol}: {e}")

        # Step 4: Final manual fallback (Kite may not expose some indices)
        manual_index_tokens = {
            "NIFTY": 256265,
            "BANKNIFTY": 260105,
            "NIFTYIT": 9992609,
            "NIFTYAUTO": 8969473,
            "NIFTYPHARMA": 974593,
            "NIFTYFMCG": 1199361,
            "NIFTYENERGY": 1376769,
            "NIFTYFIN": 10519041,
            "NIFTYINFRA": 135049,
            "NIFTYMIDCAP100": 1287746,
            "NIFTYSMALLCAP100": 1292545
        }
        if symbol in manual_index_tokens:
            token = manual_index_tokens[symbol]
            print(f"[HARDCODE ✅] Used static token for {symbol} → {token}")
            return token

        # Step 5: Not found
        print(f"[❌] No token found for {symbol}")
        return None
        
    def fetch_historical_ohlc(self, symbol, from_date, to_date, interval="day"):
        token = self.fetch_instrument_token(symbol)
        print(f"[FETCH] {symbol} OHLC from {from_date} to {to_date} → Token: {token}")

        if not token:
            return pd.DataFrame()

        # Fresh KiteConnect session for reliable fetch
        kite = KiteConnect(api_key=self.api_key)
        kite.set_access_token(self.access_token)

        try:
            data = kite.historical_data(
                instrument_token=token,
                from_date=from_date,
                to_date=to_date,
                interval=interval
            )

            if not data:
                print(f"[EMPTY] {symbol}")
                return pd.DataFrame()

            df = pd.DataFrame(data)
            if 'close' not in df.columns:
                print(f"[ERROR] {symbol}: Missing 'close' column.")
                return pd.DataFrame()

            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
            return df

        except Exception as e:
            print(f"[FAIL] {symbol}: {e}")
            return pd.DataFrame()

    def fetch_multiple_ohlc(self, symbol_list):
        today = datetime.now().date()
        days_of_data = 50
        holiday_buffer = 30
        start = today - timedelta(days=days_of_data + holiday_buffer)
        end = today

        print(f"[INFO] Fetching OHLCV for {len(symbol_list)} symbols from {start} to {end}")
        data_dict = {}

        for symbol in symbol_list:
            df = self.fetch_historical_ohlc(symbol, start, end)
            if not df.empty:
                data_dict[symbol] = df
                print(f"[✅] {symbol}: {len(df)} rows")
            else:
                print(f"[SKIP] No data for {symbol}")
            time.sleep(0.4)  # Respect rate limits

        print(f"[✅] Fetched data for {len(data_dict)} symbols.")
        return data_dict

    def fetch_index_data(self, index_symbol='NIFTY', start=None, end=None):
        if not start or not end:
            end = datetime.now().date()
            start = end - timedelta(days=50)
        index_df = self.fetch_historical_ohlc(index_symbol, start, end)
        if index_df.empty:
            print(f"[❌] Failed to fetch index data for {index_symbol}")
        else:
            print(f"[✅] Index {index_symbol}: {len(index_df)} rows")
        return index_df
