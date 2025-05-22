import streamlit as st
import os
import sys

# Ensure the repository root is on the Python path so that the local
# `broker` package can be imported when this script is executed
# directly by Streamlit or Python.
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from broker.zerodha import ZerodhaBroker, DummyWebSocket


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


def main():
    broker = get_broker()
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
    st.subheader("Balance")
    st.write(portfolio["balance"])

    st.subheader("Holdings")
    st.write(portfolio["holdings"])

    st.subheader("Order History")
    st.write(portfolio["orders"])


if __name__ == "__main__":
    main()
