from kiteconnect import KiteConnect
from datetime import datetime, timedelta

api_key = "kut7ix3qpu48c2m1"
access_token = "pBVwMdEPfc1GIdCxGNBq0wrBqCqLtHVE"

kite = KiteConnect(api_key=api_key)
kite.set_access_token(access_token)

symbol = "RELIANCE"
token = 738561  # Known working token for RELIANCE
from_date = datetime.now().date() - timedelta(days=10)
to_date = datetime.now().date()

data = kite.historical_data(
    instrument_token=token,
    from_date=from_date,
    to_date=to_date,
    interval="day"
)

if data:
    print(f"[✅] {symbol} OHLC Data:")
    for d in data:
        print(d)
else:
    print(f"[❌] No OHLC data for {symbol}")
