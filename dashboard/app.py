import streamlit as st
from broker.zerodha import ZerodhaBroker, DummyWebSocket


@st.cache_resource
def get_broker():
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
