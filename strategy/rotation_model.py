# rs_outperformance_kite_system/strategy/rotation_model.py

from strategy.rs_exit_engine import evaluate_exit
from core.rs_calculator import compute_rs_rank
from core.pattern_recognizer import get_rs_pattern
import pandas as pd
import time

def rotate_portfolio(
    portfolio,
    stock_data_dict,
    index_df,
    rs_alpha_dict=None,
    top_rs_list=None,
    max_holdings=10,
    live_prices=None,
):
    """Rotate portfolio based on RS rank and exit signals.

    Parameters
    ----------
    portfolio : list
        Current list of held symbols.
    stock_data_dict : dict[str, pd.DataFrame]
        Historical OHLC data for the portfolio symbols.
    index_df : pd.DataFrame
        Index OHLC data used for RS calculations.
    rs_alpha_dict : dict[str, float], optional
        Mapping of symbol to latest RS Alpha value. If provided and
        ``top_rs_list`` is ``None`` the function will compute the ranking
        automatically.
    top_rs_list : list[str], optional
        Optional list of candidate RS leaders. If omitted it will be derived
        from ``rs_alpha_dict``.
    max_holdings : int
        Maximum number of holdings after rotation.
    live_prices : dict[str, float], optional
        Latest live prices from a websocket stream. When supplied the prices
        are appended to ``stock_data_dict`` before evaluating exits.
    """

    if rs_alpha_dict and top_rs_list is None:
        ranked = compute_rs_rank(rs_alpha_dict)
        top_rs_list = ranked.index.tolist()

    if top_rs_list is None:
        top_rs_list = []

    # Apply live prices to stock data if given
    if live_prices:
        ts = pd.Timestamp.now()
        for sym, price in live_prices.items():
            df = stock_data_dict.get(sym)
            if df is not None:
                df.loc[ts] = {'close': price}

    updated_portfolio = portfolio.copy()
    exit_log = []
    entry_log = []

    # Step 1: Evaluate exits
    for symbol in portfolio:
        stock_df = stock_data_dict.get(symbol)
        if stock_df is None:
            continue

        exit_signal = evaluate_exit(stock_df, index_df, symbol)
        if exit_signal or symbol not in top_rs_list:
            exit_log.append({'symbol': symbol, 'reason': exit_signal['Exit Reason'] if exit_signal else 'RS Rank dropped'})
            if symbol in updated_portfolio:
                updated_portfolio.remove(symbol)

    # Step 2: Add new top-ranked RS stocks
    for candidate in top_rs_list:
        if candidate not in updated_portfolio:
            updated_portfolio.append(candidate)
            entry_log.append({'symbol': candidate, 'reason': 'Top RS Alpha'})

        if len(updated_portfolio) >= max_holdings:
            break

    return {
        'new_portfolio': updated_portfolio,
        'exits': exit_log,
        'entries': entry_log
    }


def rotate_portfolio_live(
    portfolio,
    stock_data_dict,
    index_df,
    rs_alpha_dict,
    streamer,
    wait_time=2,
    max_holdings=10,
):
    """Rotate portfolio using live prices fetched from a websocket streamer.

    Parameters
    ----------
    streamer : LivePriceStreamer
        Instance of :class:`~data.live_fetch.kite_websocket.LivePriceStreamer`.
    wait_time : int
        Seconds to wait for ticks before processing rotation.
    """
    live_prices = {}

    def _collect(data):
        live_prices.update(data)

    streamer.start(list(portfolio), _collect)
    time.sleep(wait_time)
    streamer.stop()

    return rotate_portfolio(
        portfolio,
        stock_data_dict,
        index_df,
        rs_alpha_dict=rs_alpha_dict,
        top_rs_list=None,
        max_holdings=max_holdings,
        live_prices=live_prices,
    )
