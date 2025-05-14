# rs_outperformance_kite_system/strategy/rs_exit_engine.py

from core.rs_calculator import compute_rs_alpha, add_ama, add_donchian_channel
from core.pattern_recognizer import get_rs_pattern
import pandas as pd

def evaluate_exit(stock_df, index_df, symbol, rs_threshold=0.01):
    """Return True if exit is suggested"""
    rs_series = stock_df['close'] / index_df['close']
    rs_alpha_series = compute_rs_alpha(stock_df, index_df)
    latest_rs = rs_alpha_series.dropna().iloc[-1]

    pattern = get_rs_pattern(rs_series)
    stock_df = add_ama(stock_df)
    stock_df = add_donchian_channel(stock_df)

    close = stock_df['close'].iloc[-1]
    ama = stock_df['ama'].iloc[-1]
    donchian_signal = stock_df['donchian_breakout'].iloc[-1]

    ema50 = stock_df['close'].rolling(window=50).mean().iloc[-1]

    if latest_rs < rs_threshold:
        reason = "RS Alpha weak"
    elif pattern in ["Drowning", "Cat"]:
        reason = f"RS pattern = {pattern}"
    elif close < ama:
        reason = "Price below AMA"
    elif donchian_signal == -1:
        reason = "Donchian breakdown"
    elif close < ema50:
        reason = "Price below 50 EMA"
    else:
        return None  # No exit

    return {
        "symbol": symbol,
        "RS Alpha": latest_rs,
        "RS Pattern": pattern,
        "Price": close,
        "AMA": ama,
        "Exit Reason": reason
    }

def check_exit_signals(portfolio, stock_data_dict, index_df):
    """Evaluate exit signals for a given portfolio"""
    exit_list = []

    for symbol in portfolio:
        stock_df = stock_data_dict.get(symbol)
        if stock_df is not None:
            result = evaluate_exit(stock_df, index_df, symbol)
            if result:
                exit_list.append(result)

    return pd.DataFrame(exit_list)
