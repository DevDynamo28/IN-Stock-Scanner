import streamlit as st
import os
import sys
import glob
import random

# Ensure the repository root is on the Python path so that the local
# `broker` package can be imported when this script is executed
# directly by Streamlit or Python.
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from broker.zerodha import ZerodhaBroker, DummyWebSocket
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
            broker.place_order(symbol, 1, entry_price, 'buy')
            positions[symbol] = {
                'entry': entry_price,
                'target': target_price,
            }

    # Exit positions no longer on the watchlist or hitting target
    for symbol in list(positions.keys()):
        info = positions[symbol]
        current_price = random.uniform(50, 150)

        if symbol not in watchlist or current_price >= info['target']:
            broker.place_order(symbol, 1, current_price, 'sell')
            del positions[symbol]


def main():
    broker = get_broker()
    watchlist = load_latest_watchlist()
    auto_manage_positions(broker, watchlist)

    st.title("Paper Trading Dashboard")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Deposit 10000"):
            broker.deposit(10000)
    with col2:
        if st.button("Withdraw 1000"):
            try:
                broker.withdraw(1000)
            except ValueError as e:
                st.error(str(e))

    portfolio = broker.get_portfolio()
    st.subheader("Current Watchlist")
    st.write(watchlist)
    st.subheader("Balance")
    st.write(portfolio["balance"])

    st.subheader("Open Positions")
    st.write(st.session_state.get('positions', {}))

    st.subheader("Holdings")
    st.write(portfolio["holdings"])

    st.subheader("Order History")
    st.write(portfolio["orders"])


if __name__ == "__main__":
    main()
