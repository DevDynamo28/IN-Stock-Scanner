import pandas as pd
import yaml
from core.rs_calculator import compute_rs_alpha

# Load sector mapping from YAML file
with open("config/sector_map.yaml", "r") as f:
    sector_map = yaml.safe_load(f)

def filter_by_sector_strength(stock_data_dict, index_data_dict, top_n_sectors=3):
    """
    Ranks sectors by RS Alpha (via ETF proxies) and returns stock symbols from top N sectors.
    """
    sector_rs = {}

    # Step 1: Calculate RS Alpha for each sector ETF proxy
    for sector, index_df in index_data_dict.items():
        if index_df is not None and not index_df.empty:
            for stock, df in stock_data_dict.items():
                if df is not None and not df.empty:
                    rs = compute_rs_alpha(df, index_df)
                    if not rs.empty:
                        sector_rs[sector] = rs.iloc[-1]  # use last RS Alpha
                    break

    # Step 2: Rank sectors by RS
    top_sectors = sorted(sector_rs.items(), key=lambda x: x[1], reverse=True)[:top_n_sectors]
    top_sector_names = [s[0] for s in top_sectors]
    print(f"[✅] Top Sectors by RS: {top_sector_names}")

    # Step 3: Filter stock symbols based on sector_map
    selected_symbols = []
    for stock in stock_data_dict:
        stock_sector = sector_map.get(stock)
        if stock_sector in top_sector_names:
            selected_symbols.append(stock)

    return selected_symbols