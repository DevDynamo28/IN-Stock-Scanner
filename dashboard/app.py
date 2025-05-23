import streamlit as st
import os
import sys
import random
import pandas as pd

# Ensure the repository root is on the Python path
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from broker.zerodha import ZerodhaBroker
from tools.watchlist import load_latest_watchlist
from data.live_fetch.kite_client import ZerodhaKiteClient
from data.live_fetch.kite_websocket import LivePriceStreamer
from tools.secrets import load_secrets

# Handle caching for compatibility across Streamlit versions
if hasattr(st, "cache_resource"):
    cache_decorator = st.cache_resource
else:
    cache_decorator = st.cache(allow_output_mutation=True)

@cache_decorator
def get_broker():
    """Return a cached ZerodhaBroker instance."""
    return ZerodhaBroker(mode="paper")

@cache_decorator
def get_kite_client():
    """Return a cached ZerodhaKiteClient for live price queries."""
    secrets = load_secrets()
    return ZerodhaKiteClient(
        secrets.get("kite_api_key"),
        secrets.get("kite_api_secret"),
        secrets.get("kite_access_token"),
    )

@cache_decorator
def get_price_streamer():
    """Return a cached LivePriceStreamer for websocket price snapshots."""
    secrets = load_secrets()
    client = ZerodhaKiteClient(
        secrets.get("kite_api_key"),
        secrets.get("kite_api_secret"),
        secrets.get("kite_access_token"),
    )
    return LivePriceStreamer(
        secrets.get("kite_api_key"),
        secrets.get("kite_access_token"),
        client.instrument_cache,
    )

def get_live_prices(symbols):
    """Return a mapping of symbol to the latest live price.

    If fetching live prices fails (e.g. due to missing credentials or
    network issues) random values are returned as a fallback so the
    dashboard remains functional in offline environments.
    """
    # First try fetching via websocket snapshot
    streamer = get_price_streamer()
    try:
        prices = streamer.snapshot(list(symbols), timeout=1)
        if prices:
            return prices
    except Exception as e:  # pragma: no cover - websocket/network issue
        st.warning(f"Live stream failed: {e}")

    client = get_kite_client()
    try:
        prices = client.fetch_live_prices(list(symbols))
        if prices:
            return prices
    except Exception as e:  # pragma: no cover - network issue
        st.warning(f"Live price fetch failed: {e}")
    return {s: round(random.uniform(50, 150), 2) for s in symbols}

def auto_manage_positions(broker, watchlist, live_prices):
    """Automatically manage paper positions based on the watchlist."""
    if 'positions' not in st.session_state:
        st.session_state['positions'] = {}

    positions = st.session_state['positions']

    # Enter new symbols
    for symbol in watchlist:
        if symbol not in positions:
            entry_price = live_prices.get(symbol, round(random.uniform(50, 150), 2))
            target_price = round(entry_price * 1.1, 2)
            try:
                broker.place_order(symbol, 1, entry_price, 'buy')
                positions[symbol] = {
                    'entry': entry_price,
                    'target': target_price,
                }
            except ValueError as e:
                st.warning(f"Failed to buy {symbol}: {e}")

    # Exit positions no longer in watchlist or that hit target
    for symbol in list(positions.keys()):
        info = positions[symbol]
        current_price = live_prices.get(symbol, round(random.uniform(50, 150), 2))
        if symbol not in watchlist or current_price >= info['target']:
            try:
                broker.place_order(symbol, 1, current_price, 'sell')
                del positions[symbol]
            except ValueError as e:
                st.warning(f"Failed to sell {symbol}: {e}")

def main():
    broker = get_broker()
    watchlist = load_latest_watchlist()
    # Fetch live prices for watchlist and current positions
    portfolio = broker.get_portfolio()
    positions = st.session_state.get("positions", {})
    symbols_for_prices = set(watchlist).union(positions.keys(), portfolio["holdings"].keys())
    live_prices = get_live_prices(symbols_for_prices)
    auto_manage_positions(broker, watchlist, live_prices)
    portfolio = broker.get_portfolio()
    positions = st.session_state.get("positions", {})

    st.title("📊 Paper Trading Dashboard")

    # Deposit/Withdraw controls
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Deposit ₹10,000"):
            broker.deposit(10000)
            st.success("Deposited ₹10,000")
    with col2:
        if st.button("Withdraw ₹1,000"):
            try:
                broker.withdraw(1000)
                st.success("Withdrew ₹1,000")
            except ValueError as e:
                st.error(str(e))

    # Account Metrics
    st.subheader("Account Overview")
    mcol1, mcol2, mcol3 = st.columns(3)
    mcol1.metric("Balance", f"{portfolio['balance']:.2f}")
    mcol2.metric("Holdings", len(portfolio["holdings"]))
    mcol3.metric("Open Positions", len(positions))

    # Watchlist
    st.subheader("Current Watchlist")
    if watchlist:
        wl_df = pd.DataFrame({
            "Symbol": watchlist,
            "Live Price": [live_prices.get(s, 0.0) for s in watchlist],
        })
        st.table(wl_df)
    else:
        st.write("No symbols in watchlist.")

    # Open Positions
    st.subheader("Open Positions")
    if positions:
        pos_data = []
        for sym, info in positions.items():
            current = live_prices.get(sym, 0.0)
            pnl = round(current - info["entry"], 2)
            pos_data.append({
                "Symbol": sym,
                "Entry": info["entry"],
                "Target": info["target"],
                "Live Price": current,
                "PnL": pnl,
            })
        st.table(pd.DataFrame(pos_data))
    else:
        st.write("No open positions.")

    # Holdings
    st.subheader("Holdings")
    holdings = portfolio["holdings"]
    if holdings:
        hold_data = []
        for sym, info in holdings.items():
            qty = info["qty"]
            avg_price = info["avg_price"]
            current = live_prices.get(sym, 0.0)
            pnl = round((current - avg_price) * qty, 2)
            hold_data.append({
                "Symbol": sym,
                "Qty": qty,
                "Avg Price": avg_price,
                "Live Price": current,
                "PnL": pnl,
            })
        st.table(pd.DataFrame(hold_data))
    else:
        st.write("No holdings.")

    # Orders
    st.subheader("Order History")
    orders = portfolio["orders"]
    if orders:
        st.table(pd.DataFrame(orders))
    else:
        st.write("No orders yet.")

if __name__ == "__main__":
    main()
