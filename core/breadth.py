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


# rs_outperformance_kite_system/core/sector_analysis.py

import pandas as pd
from core.rs_calculator import compute_rs_alpha

def filter_by_sector_strength(stock_data_dict, index_data_dict, top_n_sectors=3):
    """
    Ranks sectors by RS Alpha and returns stock symbols from top N sectors.
    """
    sector_rs = {}

    for sector, index_df in index_data_dict.items():
        if index_df is not None and not index_df.empty:
            # Use one random stock from that sector for RS comparison
            for stock, df in stock_data_dict.items():
                if df is not None and not df.empty:
                    rs = compute_rs_alpha(df, index_df)
                    if not rs.empty:
                        sector_rs[sector] = rs.iloc[-1]  # Use latest RS Alpha
                    break

    # Rank sectors
    top_sectors = sorted(sector_rs.items(), key=lambda x: x[1], reverse=True)[:top_n_sectors]
    top_sector_names = [s[0] for s in top_sectors]
    print(f"[✅] Top Sectors by RS: {top_sector_names}")

    # Filter stock symbols from these sectors
    selected_symbols = []
    for stock in stock_data_dict:
        for sector in top_sector_names:
            if stock.startswith(sector):  # This is placeholder logic
                selected_symbols.append(stock)
                break

    return selected_symbols
