import os
import sys
from datetime import datetime, date

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
st.set_page_config(page_title="📊 Zerodha Live Dashboard", layout="wide")

import pandas as pd
from kiteconnect import KiteConnect
from tools.secrets import load_secrets

# --- Load credentials ---
secrets = load_secrets()
api_key = secrets["kite_api_key"]
access_token = secrets["kite_access_token"]

# --- Init Kite client ---
kite = KiteConnect(api_key=api_key)
kite.set_access_token(access_token)

st.title("📊 Zerodha Live Dashboard")

# --- 📦 Live Positions ---
try:
    positions = kite.positions()["net"]
    data = []
    total_unrealized = 0

    for pos in positions:
        if pos["quantity"] == 0:
            continue
        pnl = pos["pnl"]
        total_unrealized += pnl
        data.append({
            "Symbol": pos["tradingsymbol"],
            "Qty": pos["quantity"],
            "Avg Price": round(pos["average_price"], 2),
            "LTP": round(pos["last_price"], 2),
            "P&L": round(pnl, 2)
        })

    st.subheader("📦 Open Positions")
    if data:
        df = pd.DataFrame(data)
        st.dataframe(df.style.format({"Avg Price": "₹{:.2f}", "LTP": "₹{:.2f}", "P&L": "₹{:.2f}"}))
    else:
        st.info("No open positions.")

except Exception as e:
    st.error(f"❌ Error fetching positions: {e}")

# --- 💰 Funds Info ---
try:
    margin = kite.margins()["equity"]
    st.subheader("💰 Funds Overview")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Available Cash", f"₹{margin['available']['cash']:.2f}")
    col2.metric("Used Margin", f"₹{margin['utilised']['debits']:.2f}")
    col3.metric("Total Available", f"₹{margin['available']['live_balance']:.2f}")
    col4.metric("Net", f"₹{margin['net']:.2f}")

except Exception as e:
    st.error(f"❌ Error fetching funds: {e}")

# --- 📈 Today’s P&L ---
try:
    st.subheader("📈 Today’s P&L")
    realised = sum([p["realised"] for p in positions])
    unrealised = sum([p["unrealised"] for p in positions])
    st.write(f"**Realized P&L:** ₹{realised:.2f}")
    st.write(f"**Unrealized P&L:** ₹{unrealised:.2f}")
    st.write(f"**Total P&L:** ₹{realised + unrealised:.2f}")
except Exception as e:
    st.warning("P&L data unavailable.")

# --- 🧾 Today’s Order History ---
try:
    st.subheader("🧾 Today’s Orders")

    orders = kite.orders()
    today = date.today()
    today_orders = []

    for order in orders:
        ts = pd.to_datetime(order["order_timestamp"])
        if ts.date() == today:
            today_orders.append({
                "Time": ts.strftime("%H:%M:%S"),
                "Symbol": order["tradingsymbol"],
                "Qty": order["quantity"],
                "Type": order["transaction_type"],
                "Status": order["status"],
                "Price": round(order["average_price"] or 0.0, 2)
            })

    if today_orders:
        df_orders = pd.DataFrame(today_orders)
        st.dataframe(df_orders)
    else:
        st.info("No orders today.")

except Exception as e:
    st.error(f"❌ Error fetching order book: {e}")
