import streamlit as st
import pandas as pd
from alpaca.trading.client import TradingClient

# PAGE SETTINGS
st.set_page_config(layout="wide")

st.title("Trading Dashboard")

# LOAD SECRETS
API_KEY = st.secrets["API_KEY"]
SECRET_KEY = st.secrets["SECRET_KEY"]

# IMPORTANT:
# paper=False for LIVE account
# paper=True for PAPER account
client = TradingClient(
    API_KEY,
    SECRET_KEY,
    paper=False
)

# TRY CONNECTING TO ALPACA
try:
    account = client.get_account()

except Exception as e:
    st.error("Alpaca Connection Error")
    st.write(e)
    st.stop()

# ACCOUNT DATA
equity = float(account.equity)
cash = float(account.cash)
buying_power = float(account.buying_power)

# METRICS
col1, col2, col3 = st.columns(3)

col1.metric(
    "Equity",
    f"${equity:,.2f}"
)

col2.metric(
    "Cash",
    f"${cash:,.2f}"
)

col3.metric(
    "Buying Power",
    f"${buying_power:,.2f}"
)

# POSITIONS
st.subheader("Open Positions")

positions = client.get_all_positions()

if positions:

    position_data = []

    for p in positions:

        position_data.append({
            "Symbol": p.symbol,
            "Qty": p.qty,
            "Market Value": round(float(p.market_value), 2),
            "Unrealized PnL": round(float(p.unrealized_pl), 2),
            "Side": p.side
        })

    positions_df = pd.DataFrame(position_data)

    st.dataframe(
        positions_df,
        use_container_width=True
    )

else:
    st.write("No open positions")

# SIMPLE EQUITY GRAPH
st.subheader("Equity Curve")

equity_history = pd.DataFrame({
    "Equity": [
        2000,
        2015,
        2025,
        2040,
        equity
    ]
})

st.line_chart(equity_history)

# RECENT ORDERS
st.subheader("Recent Orders")

try:

    orders = client.get_orders()

    order_data = []

    for o in orders[:10]:

        order_data.append({
            "Symbol": o.symbol,
            "Side": o.side,
            "Qty": o.qty,
            "Status": o.status
        })

    orders_df = pd.DataFrame(order_data)

    st.dataframe(
        orders_df,
        use_container_width=True
    )

except Exception as e:
    st.write("Could not load orders")
    st.write(e)

st.success("Dashboard Connected Successfully")
