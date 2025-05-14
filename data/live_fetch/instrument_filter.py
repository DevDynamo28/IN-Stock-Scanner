# rs_outperformance_kite_system/data/live_fetch/instrument_filter.py

from kiteconnect import KiteConnect
import pandas as pd
import re

def is_valid_symbol(s):
    """Check if symbol is uppercase letters only (e.g., TCS, INFY)."""
    return bool(re.match(r'^[A-Z]{2,}$', s))

def get_filtered_instruments(kite, max_count=300):
    try:
        instruments = kite.instruments("NSE")
        df = pd.DataFrame(instruments)

        # Step 1: Filter for EQ stocks only
        df = df[
            (df['segment'] == 'NSE') &
            (df['instrument_type'] == 'EQ') &
            (df['exchange'] == 'NSE')
        ]

        # Step 2: Remove junk suffixes
        blacklist_suffixes = ['-GB', '-BE', '-SM', '-BZ', '-GS', '-N1', '-N2', '-PP']
        for suffix in blacklist_suffixes:
            df = df[~df['tradingsymbol'].str.endswith(suffix)]

        # Step 3: Validate symbol format (remove bonds, G-Secs, etc.)
        df = df[df['tradingsymbol'].apply(is_valid_symbol)]

        # Step 4: Sort and truncate
        df = df.sort_values('tradingsymbol')
        symbols = df['tradingsymbol'].drop_duplicates().tolist()[:max_count]

        print(f"[✅] Filtered {len(symbols)} clean EQ stocks for RS scan.")
        return symbols

    except Exception as e:
        print(f"[❌] Error in filtering instruments: {e}")
        return []
