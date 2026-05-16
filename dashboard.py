import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from alpaca.trading.client import TradingClient
from datetime import datetime

# =====================================
# PAGE CONFIG
# =====================================

st.set_page_config(
    page_title="Trading Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================
# CUSTOM CSS
# =====================================

st.markdown(
    """
    <style>

    .main {
        background-color: #0E1117;
    }

    h1, h2, h3 {
        color: white;
    }

    .stMetric {
        background-color: #1E2633;
        padding: 15px;
        border-radius: 15px;
        border: 1px solid #2D3748;
    }

    .stDataFrame {
        border-radius: 12px;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# =====================================
# TITLE
# =====================================

st.title("📈 Advanced Trading Dashboard")

# =====================================
# LOAD SECRETS
# =====================================

API_KEY = st.secrets["API_KEY"]
SECRET_KEY = st.secrets["SECRET_KEY"]

# =====================================
# CONNECT TO ALPACA
# =====================================

client = TradingClient(
    API_KEY,
    SECRET_KEY,
    paper=False
)

# =====================================
# GET ACCOUNT
# =====================================

try:
    account = client.get_account()
except Exception as e:
    st.error("Alpaca Connection Error")
    st.write(e)
    st.stop()

# =====================================
# ACCOUNT VALUES
# =====================================

equity = float(account.equity)
cash = float(account.cash)
buying_power = float(account.buying_power)
portfolio_value = float(account.portfolio_value)

# =====================================
# DAILY PNL
# =====================================

try:
    last_equity = float(account.last_equity)
    daily_pnl = equity - last_equity
    daily_pnl_pct = (daily_pnl / last_equity) * 100
except:
    daily_pnl = 0
    daily_pnl_pct = 0

# =====================================
# METRICS
# =====================================

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Equity",
    f"${equity:,.2f}",
    f"{daily_pnl_pct:.2f}%"
)

col2.metric(
    "Cash",
    f"${cash:,.2f}"
)

col3.metric(
    "Buying Power",
    f"${buying_power:,.2f}"
)

col4.metric(
    "Daily PnL",
    f"${daily_pnl:,.2f}"
)

st.divider()

# =====================================
# POSITIONS
# =====================================

st.subheader("📦 Open Positions")

positions = client.get_all_positions()

if positions:

    position_data = []

    total_unrealized = 0

    for p in positions:

        unrealized = float(p.unrealized_pl)
        total_unrealized += unrealized

        position_data.append({
            "Symbol": p.symbol,
            "Qty": float(p.qty),
            "Current Price": round(float(p.current_price), 2),
            "Market Value": round(float(p.market_value), 2),
            "Unrealized PnL": round(unrealized, 2),
            "Unrealized %": round(float(p.unrealized_plpc) * 100, 2)
        })

    positions_df = pd.DataFrame(position_data)

    st.dataframe(
        positions_df,
        use_container_width=True,
        hide_index=True
    )

    st.success(f"Total Unrealized PnL: ${total_unrealized:,.2f}")

else:
    st.info("No open positions")

st.divider()

# =====================================
# POSITION PIE CHART
# =====================================

if positions:

    st.subheader("🥧 Portfolio Allocation")

    pie_df = pd.DataFrame(position_data)

    fig_pie = px.pie(
        pie_df,
        names="Symbol",
        values="Market Value",
        hole=0.5
    )

    fig_pie.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0E1117",
        plot_bgcolor="#0E1117"
    )

    st.plotly_chart(fig_pie, use_container_width=True)

st.divider()

# =====================================
# EQUITY CURVE
# =====================================

st.subheader("📊 Equity Curve")

history = [
    equity * 0.95,
    equity * 0.96,
    equity * 0.97,
    equity * 0.985,
    equity
]

history_df = pd.DataFrame({
    "Step": [1, 2, 3, 4, 5],
    "Equity": history
})

fig_equity = go.Figure()

fig_equity.add_trace(
    go.Scatter(
        x=history_df["Step"],
        y=history_df["Equity"],
        mode="lines+markers",
        name="Equity"
    )
)

fig_equity.update_layout(
    template="plotly_dark",
    paper_bgcolor="#0E1117",
    plot_bgcolor="#0E1117",
    xaxis_title="Time",
    yaxis_title="Account Equity",
    height=500
)

st.plotly_chart(fig_equity, use_container_width=True)

st.divider()

# =====================================
# ORDERS
# =====================================

st.subheader("🧾 Recent Orders")

try:

    orders = client.get_orders()

    order_data = []

    for o in orders[:20]:

        order_data.append({
            "Symbol": o.symbol,
            "Side": str(o.side).upper(),
            "Qty": o.qty,
            "Type": o.order_type,
            "Status": o.status,
            "Created": o.created_at
        })

    orders_df = pd.DataFrame(order_data)

    st.dataframe(
        orders_df,
        use_container_width=True,
        hide_index=True
    )

except Exception as e:
    st.warning("Could not load recent orders")
    st.write(e)

st.divider()

# =====================================
# PERFORMANCE SECTION
# =====================================

st.subheader("📈 Performance Stats")

perf1, perf2, perf3, perf4 = st.columns(4)

perf1.metric(
    "Portfolio Value",
    f"${portfolio_value:,.2f}"
)

perf2.metric(
    "Today's Return",
    f"{daily_pnl_pct:.2f}%"
)

perf3.metric(
    "Open Positions",
    len(positions)
)

perf4.metric(
    "Account Status",
    str(account.status).upper()
)

st.divider()

# =====================================
# SIDEBAR
# =====================================

st.sidebar.title("⚙ Dashboard Controls")

st.sidebar.success("Connected to Alpaca Live Account")

st.sidebar.write(
    f"Last Refresh:\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
)

st.sidebar.info(
    "Future upgrades:\n"
    "- Real equity history\n"
    "- Win rate tracking\n"
    "- Trade analytics\n"
    "- AI trade summaries\n"
    "- Risk metrics\n"
    "- Discord alerts"
)

# =====================================
# FOOTER
# =====================================

st.success("Dashboard Connected Successfully")
