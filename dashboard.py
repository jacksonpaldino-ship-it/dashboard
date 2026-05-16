import streamlit as st
import pandas as pd
from alpaca.trading.client import TradingClient

# STREAMLIT PAGE
st.set_page_config(layout="wide")

st.title("Trading Dashboard")

# ALPACA KEYS
API_KEY = st.secrets["API_KEY"]
SECRET_KEY = st.secrets["SECRET_KEY"]

# CONNECT
client = TradingClient(API_KEY, SECRET_KEY, paper=False)

# ACCOUNT
account = client.get_account()

equity = float(account.equity)
cash = float(account.cash)

# METRICS
col1, col2 = st.columns(2)

col1.metric("Equity", f"${equity:,.2f}")
col2.metric("Cash", f"${cash:,.2f}")

# POSITIONS
positions = client.get_all_positions()

st.subheader("Open Positions")

if positions:
    data = []

    for p in positions:
        data.append({
            "Symbol": p.symbol,
            "Qty": p.qty,
            "Market Value": float(p.market_value),
            "Unrealized PnL": float(p.unrealized_pl)
        })

    df = pd.DataFrame(data)

    st.dataframe(df, use_container_width=True)

else:
    st.write("No open positions")

# SIMPLE EQUITY GRAPH
history = [2000, 2010, 2025, 2035, equity]

chart_df = pd.DataFrame({
    "Equity": history
})

st.subheader("Equity Curve")

st.line_chart(chart_df)
