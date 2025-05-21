# rs_outperformance_kite_system/core/breadth.py

import pandas as pd

def evaluate_breadth(stock_data_dict, ma_days=50, threshold=0.55):
    """
    Checks if market breadth is strong based on % stocks above MA.
    """
    count_above = 0
    total = 0

    for df in stock_data_dict.values():
        if len(df) >= ma_days:
            ma = df['close'].rolling(ma_days).mean()
            if df['close'].iloc[-1] > ma.iloc[-1]:
                count_above += 1
            total += 1

    if total == 0:
        print("[❌] Breadth check failed: No valid stocks.")
        return False

    percent = count_above / total
    print(f"[📊] Market breadth: {percent:.2%} stocks above {ma_days}-day MA")
    return percent >= threshold
