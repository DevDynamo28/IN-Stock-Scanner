# rs_outperformance_kite_system/core/pattern_recognizer.py

import numpy as np
import pandas as pd

def detect_flying_pattern(rs_series, window=10):
    """Higher highs and higher lows in RS = Flying"""
    df = pd.DataFrame(rs_series, columns=['rs'])
    df['hh'] = df['rs'] > df['rs'].shift(1)
    df['hl'] = df['rs'].rolling(window).min().shift(1) < df['rs']
    if df['hh'].iloc[-window:].sum() >= (window * 0.7) and df['hl'].iloc[-1]:
        return True
    return False

def detect_lion_pattern(rs_series, spike_threshold=0.05):
    """Sudden RS jump = Lion"""
    diff = rs_series.diff()
    avg = diff.rolling(5).mean()
    if diff.iloc[-1] > spike_threshold and diff.iloc[-1] > (avg.iloc[-5:-1].mean() * 2):
        return True
    return False

def detect_star_pattern(rs_series, base_window=20):
    """Flat base followed by slow uptrend = Star"""
    # Use position based indexing as rs_series likely has a DateTime index
    base_std = rs_series.iloc[-base_window:-10].std()
    recent_trend = rs_series.iloc[-10:].diff().mean()
    if base_std < 0.01 and recent_trend > 0:
        return True
    return False

def detect_drowning_pattern(rs_series):
    """Steady RS decline = Drowning"""
    # iloc avoids KeyError when series index is not RangeIndex
    return rs_series.iloc[-5:].is_monotonic_decreasing

def detect_cat_pattern(rs_series, threshold=0.01):
    """Flat RS range = Cat on the wall"""
    rs_range = rs_series.iloc[-10:].max() - rs_series.iloc[-10:].min()
    return rs_range < threshold

def get_rs_pattern(rs_series):
    """Apply all recognizers and return pattern label"""
    if detect_flying_pattern(rs_series):
        return "Flying"
    elif detect_lion_pattern(rs_series):
        return "Lion"
    elif detect_star_pattern(rs_series):
        return "Star"
    elif detect_drowning_pattern(rs_series):
        return "Drowning"
    elif detect_cat_pattern(rs_series):
        return "Cat"
    else:
        return "Unclassified"
