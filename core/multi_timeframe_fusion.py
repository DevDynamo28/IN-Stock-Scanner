# core/multi_timeframe_fusion.py

import pandas as pd
from core.rs_calculator import compute_rs_alpha
from core.rs_calculator import add_ama, add_donchian_channel
from core.pattern_recognizer import get_rs_pattern


def compute_fusion_score(daily_df, weekly_df, index_daily, index_weekly):
    score = 0

    # Step 1: RS Alpha (daily)
    rs_daily = compute_rs_alpha(daily_df, index_daily).dropna()
    if len(rs_daily) > 20:
        score += 1

    # Step 2: RS Alpha (weekly)
    rs_weekly = compute_rs_alpha(weekly_df, index_weekly).dropna()
    if len(rs_weekly) > 20:
        score += 1

    # Step 3: Pattern Match (daily)
    if not rs_daily.empty:
        pattern = get_rs_pattern(rs_daily)
        if pattern in ["Flying", "Star", "Lion"]:
            score += 1

    # Step 4: Breakout & Trend Confirmation
    daily_df = add_ama(daily_df)
    daily_df = add_donchian_channel(daily_df)

    close = daily_df['close'].iloc[-1]
    ama = daily_df['ama'].iloc[-1]
    donchian = daily_df['donchian_breakout'].iloc[-1]

    if close > ama:
        score += 1
    if donchian == 1:
        score += 1

    return score  # Max score = 5


def resample_to_weekly(df):
    return df.resample('W').agg({
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum'
    }).dropna()
