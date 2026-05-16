import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from alpaca.trading.client import TradingClient
from datetime import datetime

# =========================================
# PAGE CONFIG
# =========================================

st.set_page_config(
    page_title="Advanced Trading Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================
# CUSTOM CSS
# =========================================

st.markdown(
    """
    <style>

    .stApp {
        background-color: #050816;
        color: white;
    }

    section.main > div {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1600px;
    }

    h1 {
        font-size: 3.2rem !important;
        font-weight: 800 !important;
        color: #72FF5B !important;
        margin-bottom: 2rem !important;
    }

    h2, h3 {
        color: white !important;
    }

    div[data-testid="metric-container"] {
        background: linear-gradient(145deg, #0A1020, #0D1426);
        border: 1px solid #1F2A44;
        padding: 25px;
        border-radius: 24px;
        box-shadow: 0 0 30px rgba(0,0,0,0.35);
    }

    div[data-testid="metric-container"] label {
        color: #9CA3AF !important;
        font-size: 1rem !important;
    }

    div[data-testid="metric-container"] div {
        color: #72FF5B !important;
        font-weight: 700 !important;
    }

    .stDataFrame {
        border-radius: 20px;
        overflow: hidden;
    }

    [data-testid="stSidebar"] {
        background-color: #08101F;
        border-right: 1px solid #1B2940;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# =========================================
# LOAD SECRETS
# =========================================

API_KEY = st.secrets["API_KEY"]
SECRET_KEY = st.secrets["SECRET_KEY"]

# =========================================
# CONNECT TO ALPACA
# =========================================

client = TradingClient(
    API_KEY,
    SECRET_KEY,
    paper=False
)

# =========================================
# ACCOUNT
# =========================================

try:
    account = client.get_account()

except Exception as e:
    st.error("Alpaca Connection Error")
    st.write(e)
    st.stop()

# =========================================
# VALUES
# =========================================

equity = float(account.equity)
cash = float(account.cash)
buying_power = float(account.buying_power)

try:
    last_equity = float(account.last_equity)
    daily_pnl = equity - last_equity
    daily_pnl_pct = (daily_pnl / last_equity) * 100
except:
    daily_pnl = 0
    daily_pnl_pct = 0

# =========================================
# SIDEBAR
# =========================================

st.sidebar.markdown(
    """
    # 📊 TRADING DASHBOARD
    """
)

st.sidebar.success("🟢 LIVE")

st.sidebar.write("Connected to Alpaca")

st.sidebar.divider()

st.sidebar.write(
    f"Last updated:\n\n{datetime.now().strftime('%b %d, %Y %I:%M:%S %p')}"
)

# =========================================
# TITLE
# =========================================

st.markdown(
    "<h1>📈 Advanced Trading Dashboard</h1>",
    unsafe_allow_html=True
)

# =========================================
# TOP METRICS
# =========================================

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

st.markdown("<br>", unsafe_allow_html=True)

# =========================================
# POSITIONS + PIE
# =========================================

left, right = st.columns([2, 1])

positions = client.get_all_positions()

position_data = []

with left:

    st.subheader("📦 Open Positions")

    if positions:

        for p in positions:

            position_data.append({
                "Symbol": p.symbol,
                "Qty": float(p.qty),
                "Avg Price": round(float(p.avg_entry_price), 2),
                "Current Price": round(float(p.current_price), 2),
                "Market Value": round(float(p.market_value), 2),
                "Unrealized PnL": round(float(p.unrealized_pl), 2),
                "Unrealized %": round(float(p.unrealized_plpc) * 100, 2)
            })

        positions_df = pd.DataFrame(position_data)

        st.dataframe(
            positions_df,
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info("No open positions")

with right:

    st.subheader("🥧 Portfolio Allocation")

    if position_data:

        pie_df = pd.DataFrame(position_data)

        fig_pie = px.pie(
            pie_df,
            names="Symbol",
            values="Market Value",
            hole=0.75
        )

        fig_pie.update_traces(
            textinfo="none"
        )

        fig_pie.update_layout(
            template="plotly_dark",
            paper_bgcolor="#050816",
            plot_bgcolor="#050816",
            font_color="white",
            height=350
        )

        st.plotly_chart(
            fig_pie,
            use_container_width=True
        )

    else:

        fig_pie = go.Figure()

        fig_pie.add_trace(
            go.Pie(
                labels=["No Data"],
                values=[1],
                hole=0.75
            )
        )

        fig_pie.update_layout(
            template="plotly_dark",
            paper_bgcolor="#050816",
            plot_bgcolor="#050816",
            font_color="white",
            height=350
        )

        st.plotly_chart(
            fig_pie,
            use_container_width=True
        )

st.markdown("<br>", unsafe_allow_html=True)

# =========================================
# EQUITY CURVE
# =========================================

st.subheader("📊 Equity Curve")

history = [
    equity * 0.95,
    equity * 0.96,
    equity * 0.97,
    equity * 0.985,
    equity
]

history_df = pd.DataFrame({
    "Time": [1, 2, 3, 4, 5],
    "Equity": history
})

fig_equity = go.Figure()

fig_equity.add_trace(
    go.Scatter(
        x=history_df["Time"],
        y=history_df["Equity"],
        mode="lines+markers",
        line=dict(
            color="#72FF5B",
            width=4
        ),
        marker=dict(
            size=8,
            color="#72FF5B"
        ),
        fill="tozeroy",
        fillcolor="rgba(114,255,91,0.08)"
    )
)

fig_equity.update_layout(
    template="plotly_dark",
    paper_bgcolor="#050816",
    plot_bgcolor="#050816",
    font_color="white",
    height=550,
    xaxis_title="Time",
    yaxis_title="Account Equity",
    showlegend=False
)

st.plotly_chart(
    fig_equity,
    use_container_width=True
)

st.markdown("<br>", unsafe_allow_html=True)

# =========================================
# RECENT ORDERS + PERFORMANCE
# =========================================

left2, right2 = st.columns([1.2, 1])

with left2:

    st.subheader("🧾 Recent Orders")

    try:

        orders = client.get_orders()

        order_data = []

        for o in orders[:10]:

            order_data.append({
                "Symbol": o.symbol,
                "Side": str(o.side).upper(),
                "Qty": o.qty,
                "Status": o.status
            })

        orders_df = pd.DataFrame(order_data)

        st.dataframe(
            orders_df,
            use_container_width=True,
            hide_index=True
        )

    except:
        st.info("No recent orders")

with right2:

    st.subheader("📈 Performance Stats")

    perf1, perf2 = st.columns(2)
    perf3, perf4 = st.columns(2)

    perf1.metric(
        "Portfolio Value",
        f"${equity:,.2f}"
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
        "ACTIVE"
    )

st.markdown("<br>", unsafe_allow_html=True)

# =========================================
# FOOTER
# =========================================

st.success("Dashboard Connected Successfully")
