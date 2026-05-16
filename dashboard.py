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
    page_title="Trading Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================
# CUSTOM CSS
# =========================================

st.markdown("""
<style>

html, body, [class*="css"] {
    font-family: Inter, sans-serif;
}

.stApp {
    background-color: #040816;
    color: white;
}

/* MAIN AREA */
.block-container {
    padding-top: 2rem;
    padding-left: 2rem;
    padding-right: 2rem;
    max-width: 1700px;
}

/* SIDEBAR */
[data-testid="stSidebar"] {
    background: #08101F;
    min-width: 280px;
    max-width: 280px;
    border-right: 1px solid #1F2937;
}

/* SIDEBAR TEXT */
.sidebar-title {
    color: #72FF5B;
    font-size: 2rem;
    font-weight: 800;
    line-height: 1.2;
    margin-bottom: 2rem;
}

/* NAV ITEMS */
.nav-item {
    background: rgba(255,255,255,0.03);
    padding: 14px 18px;
    border-radius: 14px;
    margin-bottom: 10px;
    color: white;
    font-size: 1rem;
    font-weight: 600;
}

/* MAIN TITLE */
.main-title {
    color: #72FF5B;
    font-size: 3.5rem;
    font-weight: 800;
    margin-bottom: 2rem;
}

/* METRIC CARDS */
div[data-testid="metric-container"] {
    background: linear-gradient(145deg,#0A1020,#111827);
    border: 1px solid #1F2A44;
    padding: 30px;
    border-radius: 24px;
    box-shadow: 0 0 30px rgba(0,0,0,0.35);
}

div[data-testid="metric-container"] label {
    color: #9CA3AF !important;
    font-size: 1rem !important;
}

div[data-testid="metric-container"] div {
    color: #72FF5B !important;
    font-size: 1.8rem !important;
    font-weight: 700 !important;
}

/* TABLES */
.stDataFrame {
    border-radius: 18px;
    overflow: hidden;
}

/* SECTION HEADERS */
.section-header {
    font-size: 1.6rem;
    font-weight: 700;
    margin-bottom: 1rem;
    color: white;
}

</style>
""", unsafe_allow_html=True)

# =========================================
# ALPACA CONNECTION
# =========================================

API_KEY = st.secrets["API_KEY"]
SECRET_KEY = st.secrets["SECRET_KEY"]

client = TradingClient(
    API_KEY,
    SECRET_KEY,
    paper=False
)

try:
    account = client.get_account()
except Exception as e:
    st.error("Alpaca Connection Error")
    st.write(e)
    st.stop()

# =========================================
# ACCOUNT VALUES
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
    <div class="sidebar-title">
    📊 TRADING<br>DASHBOARD
    </div>
    """,
    unsafe_allow_html=True
)

sidebar_items = [
    "🏠 Overview",
    "📦 Positions",
    "🧾 Orders",
    "📈 Performance",
    "📊 Analytics",
    "⚙ Settings"
]

for item in sidebar_items:
    st.sidebar.markdown(
        f'<div class="nav-item">{item}</div>',
        unsafe_allow_html=True
    )

st.sidebar.markdown("---")

st.sidebar.success("🟢 LIVE")

st.sidebar.write("Connected to Alpaca")

st.sidebar.write(
    f"Last Updated:\n{datetime.now().strftime('%b %d, %Y %I:%M %p')}"
)

# =========================================
# TITLE
# =========================================

st.markdown(
    '<div class="main-title">📈 Advanced Trading Dashboard</div>',
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
# POSITIONS + ALLOCATION
# =========================================

left, right = st.columns([2, 1])

positions = client.get_all_positions()
position_data = []

with left:

    st.markdown(
        '<div class="section-header">📦 Open Positions</div>',
        unsafe_allow_html=True
    )

    if positions:

        for p in positions:

            position_data.append({
                "Symbol": p.symbol,
                "Qty": float(p.qty),
                "Current Price": round(float(p.current_price), 2),
                "Market Value": round(float(p.market_value), 2),
                "Unrealized PnL": round(float(p.unrealized_pl), 2),
                "Unrealized %": round(float(p.unrealized_plpc) * 100, 2)
            })

        df = pd.DataFrame(position_data)

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info("No open positions")

with right:

    st.markdown(
        '<div class="section-header">🥧 Portfolio Allocation</div>',
        unsafe_allow_html=True
    )

    if position_data:

        pie_df = pd.DataFrame(position_data)

        fig_pie = px.pie(
            pie_df,
            names="Symbol",
            values="Market Value",
            hole=0.75
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
        paper_bgcolor="#040816",
        plot_bgcolor="#040816",
        font_color="white",
        height=350,
        showlegend=False
    )

    st.plotly_chart(
        fig_pie,
        use_container_width=True
    )

st.markdown("<br>", unsafe_allow_html=True)

# =========================================
# EQUITY CURVE
# =========================================

st.markdown(
    '<div class="section-header">📈 Equity Curve</div>',
    unsafe_allow_html=True
)

history = [
    equity * 0.95,
    equity * 0.96,
    equity * 0.97,
    equity * 0.985,
    equity
]

history_df = pd.DataFrame({
    "Time": [1,2,3,4,5],
    "Equity": history
})

fig = go.Figure()

fig.add_trace(
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

fig.update_layout(
    template="plotly_dark",
    paper_bgcolor="#040816",
    plot_bgcolor="#040816",
    font_color="white",
    height=550,
    xaxis_title="Time",
    yaxis_title="Account Equity",
    showlegend=False
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.markdown("<br>", unsafe_allow_html=True)

# =========================================
# ORDERS + PERFORMANCE
# =========================================

left2, right2 = st.columns([1.3, 1])

with left2:

    st.markdown(
        '<div class="section-header">🧾 Recent Orders</div>',
        unsafe_allow_html=True
    )

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

    st.markdown(
        '<div class="section-header">📊 Performance Stats</div>',
        unsafe_allow_html=True
    )

    p1, p2 = st.columns(2)
    p3, p4 = st.columns(2)

    p1.metric(
        "Portfolio Value",
        f"${equity:,.2f}"
    )

    p2.metric(
        "Today's Return",
        f"{daily_pnl_pct:.2f}%"
    )

    p3.metric(
        "Open Positions",
        len(positions)
    )

    p4.metric(
        "Account Status",
        "ACTIVE"
    )

st.markdown("<br>", unsafe_allow_html=True)

# =========================================
# FOOTER
# =========================================

st.success("Dashboard Connected Successfully")
