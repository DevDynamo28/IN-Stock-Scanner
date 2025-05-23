import streamlit as st
import os
import sys
import random
import pandas as pd

# Ensure the repository root is on the Python path so that the local
# `broker` package can be imported when this script is executed
# directly by Streamlit or Python.
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from broker.zerodha import ZerodhaBroker
from tools.watchlist import load_latest_watchlist


# Streamlit changed its caching API in v1.18.0. Older versions
# only provide `st.cache`, while newer versions offer
# `st.cache_resource` for long-lived objects. Support both to make
# the dashboard compatible across Streamlit releases.
if hasattr(st, "cache_resource"):
    cache_decorator = st.cache_resource
else:  # Fallback for older Streamlit versions
    cache_decorator = st.cache(allow_output_mutation=True)


@cache_decorator
def get_broker():
    """Return a cached ZerodhaBroker instance."""
    return ZerodhaBroker(mode="paper")


def get_live_prices(symbols):
    """Return a dict of simulated live prices for the given symbols."""
    return {s: round(random.uniform(50, 150), 2) for s in symbols}


def auto_manage_positions(broker, watchlist):
    """Automatically manage paper positions based on the watchlist.

    New symbols are bought immediately with a dummy price and a target 10%
    higher. Positions are sold when the symbol disappears from the watchlist
    or when a simulated price exceeds the target.
    """
    if 'positions' not in st.session_state:
        st.session_state['positions'] = {}

    positions = st.session_state['positions']

    # Enter new symbols
    for symbol in watchlist:
        if symbol not in positions:
            entry_price = random.uniform(50, 150)
            target_price = round(entry_price * 1.1, 2)
            try:
                broker.place_order(symbol, 1, entry_price, 'buy')
            except ValueError as e:
                st.warning(f"Failed to buy {symbol}: {e}")
                continue
            positions[symbol] = {
                'entry': entry_price,
                'target': target_price,
            }

    # Exit positions no longer on the watchlist or hitting target
    for symbol in list(positions.keys()):
        info = positions[symbol]
        current_price = random.uniform(50, 150)

        if symbol not in watchlist or current_price >= info['target']:
            try:
                broker.place_order(symbol, 1, current_price, 'sell')
            except ValueError as e:
                st.warning(f"Failed to sell {symbol}: {e}")
                continue
            del positions[symbol]


def main():
    broker = get_broker()
    watchlist = load_latest_watchlist()
    auto_manage_positions(broker, watchlist)

    portfolio = broker.get_portfolio()
    positions = st.session_state.get("positions", {})

    symbols_for_prices = set(watchlist)
    symbols_for_prices.update(positions.keys())
    symbols_for_prices.update(portfolio["holdings"].keys())
    live_prices = get_live_prices(symbols_for_prices)

    st.title("Paper Trading Dashboard")

    # Deposit/withdraw actions
    action_col1, action_col2 = st.columns(2)
    with action_col1:
        if st.button("Deposit 10000"):
            broker.deposit(10000)
            st.success("Deposited 10000")
    with action_col2:
        if st.button("Withdraw 1000"):
            try:
                broker.withdraw(1000)
                st.success("Withdrew 1000")
            except ValueError as e:
                st.error(str(e))

    st.subheader("Account Overview")
    mcol1, mcol2, mcol3 = st.columns(3)
    mcol1.metric("Balance", f"{portfolio['balance']:.2f}")
    mcol2.metric("Holdings", len(portfolio["holdings"]))
    mcol3.metric("Open Positions", len(positions))

    st.subheader("Current Watchlist")
    if watchlist:
        wl_df = pd.DataFrame({
            "Symbol": watchlist,
            "Live Price": [live_prices.get(s, 0) for s in watchlist],
        })
        st.table(wl_df)
    else:
        st.write("No symbols in watchlist")

    st.subheader("Open Positions")
    if positions:
        rows = []
        for sym, info in positions.items():
            current = live_prices.get(sym, 0)
            pnl = round(current - info["entry"], 2)
            rows.append({
                "Symbol": sym,
                "Entry": info["entry"],
                "Target": info["target"],
                "Live Price": current,
                "PnL": pnl,
            })
        pos_df = pd.DataFrame(rows)
        st.table(pos_df)
    else:
        st.write("No open positions")

    st.subheader("Holdings")
    holdings = portfolio["holdings"]
    if holdings:
        rows = []
        for sym, info in holdings.items():
            qty = info["qty"]
            avg_price = info["avg_price"]
            current = live_prices.get(sym, 0)
            pnl = round((current - avg_price) * qty, 2)
            rows.append({
                "Symbol": sym,
                "Qty": qty,
                "Avg Price": avg_price,
                "Live Price": current,
                "PnL": pnl,
            })
        holdings_df = pd.DataFrame(rows)
        st.table(holdings_df)
    else:
        st.write("No holdings")

    st.subheader("Order History")
    orders = portfolio["orders"]
    if orders:
        st.table(pd.DataFrame(orders))
    else:
        st.write("No orders yet")


if __name__ == "__main__":
    main()
