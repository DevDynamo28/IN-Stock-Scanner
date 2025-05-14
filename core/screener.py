# rs_outperformance_kite_system/core/screener.py

from core.rs_calculator import compute_rs_alpha, compute_rs_rank, add_ama, add_donchian_channel
from core.pattern_recognizer import get_rs_pattern
import pandas as pd

def screen_stocks(stock_data_dict, index_df, top_n=50):
    rs_alpha_latest = {}

    # Step 1: Compute RS Alpha for all stocks
    for symbol, stock_df in stock_data_dict.items():
        rs_alpha = compute_rs_alpha(stock_df, index_df)

        if rs_alpha is not None:
            rs_alpha = rs_alpha.dropna()
            if not rs_alpha.empty and len(rs_alpha) >= 21:
                rs_alpha_latest[symbol] = rs_alpha.iloc[-1]
                print(f"[RS] {symbol}: {len(rs_alpha)} RS points, latest = {rs_alpha.iloc[-1]:.4f}")
            else:
                print(f"[SKIP] No RS Alpha for {symbol} (only {len(rs_alpha)} rows)")
        else:
            print(f"[SKIP] RS Alpha failed for {symbol}")

    # Step 2: Rank top RS Alpha stocks
    rs_df = compute_rs_rank(rs_alpha_latest)
    top_symbols = rs_df.head(top_n).index.tolist()

    final_list = []

    # Step 3: Apply pattern, indicator, and price filters
    for symbol in top_symbols:
        stock_df = stock_data_dict[symbol].copy()

        if len(stock_df) < 35:
            print(f"[SKIP] {symbol} has only {len(stock_df)} rows (<35)")
            continue

        # Align stock and index for RS pattern analysis
        aligned = pd.DataFrame()
        aligned['stock'] = stock_df['close']
        aligned['index'] = index_df['close']
        aligned.dropna(inplace=True)

        if aligned.empty or len(aligned) < 21:
            print(f"[SKIP] {symbol} - insufficient aligned RS data")
            continue

        rs_series = aligned['stock'] / aligned['index']
        pattern = get_rs_pattern(rs_series)

        stock_df = add_ama(stock_df)
        stock_df = add_donchian_channel(stock_df)

        try:
            close = stock_df['close'].iloc[-1]
            ama = stock_df['ama'].iloc[-1]
            donchian_breakout = stock_df['donchian_breakout'].iloc[-1]

            if close > ama and donchian_breakout == 1 and pattern in ['Flying', 'Lion', 'Star']:
                final_list.append({
                    'symbol': symbol,
                    'RS Alpha': rs_alpha_latest[symbol],
                    'RS Pattern': pattern,
                    'Close': close,
                    'AMA': ama
                })

        except Exception as e:
            print(f"[ERROR] Filtering failed for {symbol}: {e}")

    return pd.DataFrame(final_list)