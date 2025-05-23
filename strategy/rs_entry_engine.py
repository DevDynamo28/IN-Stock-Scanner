# rs_outperformance_kite_system/strategy/rs_entry_engine.py

import pandas as pd
import yaml
from core.rs_calculator import compute_rs_alpha, compute_rs_rank, add_ama, add_donchian_channel
from core.pattern_recognizer import get_rs_pattern
from core.breadth import evaluate_breadth
from core.sector_analysis import filter_by_sector_strength
from core.multi_timeframe_fusion import compute_fusion_score, resample_to_weekly
from data.live_fetch.kite_client import ZerodhaKiteClient
from output.telegram_bot import send_telegram_message


def run_daily_entry_engine(
    api_key,
    api_secret,
    access_token,
    stock_data_dict=None,
    index_df=None,
    top_n=50,
    use_sector_filter=True,
    live_prices=None,
):
    """Run the daily RS entry scan.

    Parameters
    ----------
    live_prices : dict[str, float], optional
        Latest live prices from a websocket stream. If supplied these prices are
        appended to the OHLC data before calculating indicators.
    """

    kite = ZerodhaKiteClient(api_key, api_secret, access_token)

    # Load symbols from config
    with open("config/params.yaml") as f:
        params = yaml.safe_load(f)

    all_symbols = params['stock_list']
    index_symbol = params['index_symbol']
    top_n = params.get('top_n', 50)

    # Fetch stock data if not supplied
    if stock_data_dict is None:
        stock_data_dict = kite.fetch_multiple_ohlc(all_symbols)

    # Apply live prices if provided
    if live_prices:
        ts = pd.Timestamp.now()
        for sym, price in live_prices.items():
            if sym == index_symbol:
                # update index live price
                if index_df is not None:
                    index_df.loc[ts] = {'close': price}
                continue
            df = stock_data_dict.get(sym)
            if df is not None:
                df.loc[ts] = {'close': price}

    # ✅ Step 1: Breadth Filter
    if not evaluate_breadth(stock_data_dict):
        send_telegram_message("🚫 Market breadth is weak. Avoid new entries today.")
        return pd.DataFrame()

    # ✅ Step 2: Sector RS Filtering (optional)
    if use_sector_filter:
        sector_etf_map = {
            "NIFTYIT": "INFY",
            "NIFTYAUTO": "M&M",
            "NIFTYPHARMA": "SUNPHARMA",
            "NIFTYFMCG": "ITC",
            "NIFTYENERGY": "NTPC",
            "NIFTYFIN": "HDFCBANK",
            "NIFTYINFRA": "LT"
        }
        sector_index_data = {
            sector: stock_data_dict.get(etf_symbol)
            for sector, etf_symbol in sector_etf_map.items()
            if etf_symbol in stock_data_dict
        }

        filtered_symbols = filter_by_sector_strength(stock_data_dict, sector_index_data, top_n_sectors=3)
        print(f"[INFO] Filtered {len(filtered_symbols)} symbols after sector RS filtering.")
        stock_data_dict = {s: stock_data_dict[s] for s in filtered_symbols if s in stock_data_dict}

    # Fetch index data for RS Alpha calc if not supplied
    if index_df is None:
        index_df = kite.fetch_index_data(index_symbol)

    index_weekly = resample_to_weekly(index_df)
    results = []

    for symbol, df in stock_data_dict.items():
        if df.empty or index_df.empty:
            continue

        weekly_df = resample_to_weekly(df)
        fusion_score = compute_fusion_score(df, weekly_df, index_df, index_weekly)

        if fusion_score >= 4:
            rs_alpha = compute_rs_alpha(df, index_df).dropna()
            if len(rs_alpha) < 21:
                continue

            pattern = get_rs_pattern(rs_alpha)
            df = add_ama(df)
            df = add_donchian_channel(df)

            close = df['close'].iloc[-1]
            ama = df['ama'].iloc[-1]
            donchian_breakout = df['donchian_breakout'].iloc[-1]

            # ✅ Volume confirmation logic
            vol_confirm = False
            if 'volume' in df.columns:
                recent_volume = df['volume'].iloc[-1]
                avg_volume = df['volume'].rolling(window=20).mean().iloc[-1]
                vol_confirm = recent_volume > avg_volume

            results.append({
                'symbol': symbol,
                'RS Alpha': rs_alpha.iloc[-1],
                'RS Pattern': pattern,
                'Close': close,
                'AMA': ama,
                'Fusion Score': fusion_score,
                'Volume Confirm': vol_confirm
            })

    return pd.DataFrame(results)
