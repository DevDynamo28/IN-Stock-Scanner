# rs_outperformance_kite_system/core/rs_calculator.py

import pandas as pd

def compute_returns(df, period):
    if df.empty or 'close' not in df.columns:
        return pd.Series(dtype=float)
    return (df['close'] / df['close'].shift(period)) - 1


def compute_rs_alpha(stock_df, index_df, period=21):
    if stock_df.empty or index_df.empty:
        return pd.Series(dtype=float)

    # Step 1: Merge on date index
    combined = pd.merge(
        stock_df[['close']],
        index_df[['close']],
        how='inner',
        left_index=True,
        right_index=True,
        suffixes=('_stock', '_index')
    )

    if combined.empty or len(combined) < period + 1:
        return pd.Series(dtype=float)

    # Step 2: Compute returns
    stock_ret = (combined['close_stock'] / combined['close_stock'].shift(period)) - 1
    index_ret = (combined['close_index'] / combined['close_index'].shift(period)) - 1

    rs_alpha = stock_ret - index_ret
    return rs_alpha

def compute_rs_rank(rs_alpha_dict):
    df = pd.DataFrame.from_dict(rs_alpha_dict, orient='index', columns=['RS Alpha'])
    df = df.sort_values(by='RS Alpha', ascending=False)
    return df


def add_ama(df, period=10):
    if 'close' not in df.columns or len(df) < period:
        df['ama'] = None
        return df
    df['ama'] = df['close'].ewm(span=period, adjust=False).mean()
    return df


def add_donchian_channel(df, lookback=20):
    if len(df) < lookback:
        df['donchian_breakout'] = 0
        df['donchian_high'] = None
        df['donchian_low'] = None
        return df

    high_roll = df['high'].rolling(window=lookback).max()
    low_roll = df['low'].rolling(window=lookback).min()
    breakout = df['close'] > high_roll.shift(1)

    df['donchian_high'] = high_roll
    df['donchian_low'] = low_roll
    df['donchian_breakout'] = breakout.astype(int)
    return df