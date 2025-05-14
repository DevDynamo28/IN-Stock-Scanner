# rs_outperformance_kite_system/strategy/rotation_model.py

from strategy.rs_exit_engine import evaluate_exit
from core.rs_calculator import compute_rs_rank
from core.pattern_recognizer import get_rs_pattern

def rotate_portfolio(portfolio, stock_data_dict, index_df, rs_alpha_dict, top_rs_list, max_holdings=10):
    """
    Rotate portfolio: remove weak stocks, add new RS leaders.
    """
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
