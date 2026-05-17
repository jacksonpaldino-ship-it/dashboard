import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(
    page_title="Trading Dashboard",
    layout="wide"
)

# =========================================
# STYLE
# =========================================

st.markdown("""
<style>

html, body, [class*="css"] {
    background-color: #020617;
    color: white;
}

.block-container {
    padding-top: 2rem;
}

.metric-card {
    background: #071225;
    padding: 20px;
    border-radius: 16px;
    border: 1px solid #0f172a;
}

.green {
    color: #4ade80;
}

.sidebar .sidebar-content {
    background-color: #020617;
}

</style>
""", unsafe_allow_html=True)

# =========================================
# TITLE
# =========================================

st.markdown(
    "<h1 class='green'>📈 Advanced Trading Dashboard</h1>",
    unsafe_allow_html=True
)

st.success("Dashboard Loaded Successfully")

# =========================================
# LOAD CSV ONLY
# =========================================

csv_path = Path("equity_history.csv")

if csv_path.exists():

    df = pd.read_csv(csv_path)

else:

    df = pd.DataFrame({
        "equity": [2000, 2010, 2025, 2040, 2055]
    })

# =========================================
# METRICS
# =========================================

col1, col2, col3, col4 = st.columns(4)

latest_equity = float(df["equity"].iloc[-1])

with col1:
    st.metric("Equity", f"${latest_equity:,.2f}")

with col2:
    st.metric("Cash", f"${latest_equity:,.2f}")

with col3:
    st.metric("Buying Power", f"${latest_equity*2:,.2f}")

with col4:
    st.metric("Daily PnL", "$0.00")

# =========================================
# EQUITY CURVE
# =========================================

st.markdown("## 📈 Equity Curve")

fig = px.line(
    df,
    y="equity",
)

fig.update_traces(
    line_color="#4ade80",
    line_width=4
)

fig.update_layout(
    paper_bgcolor="#020617",
    plot_bgcolor="#020617",
    font_color="white",
    height=500
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# =========================================
# ORDERS PLACEHOLDER
# =========================================

st.markdown("## 📄 Recent Orders")

st.info("Orders loading disabled
