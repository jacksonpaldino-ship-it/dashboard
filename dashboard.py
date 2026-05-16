import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

st.title("Trading Dashboard")

equity = 2055.70
cash = 2055.70
daily_pnl = 55.12

col1, col2, col3 = st.columns(3)

col1.metric("Equity", f"${equity:,.2f}")
col2.metric("Cash", f"${cash:,.2f}")
col3.metric("Daily PnL", f"${daily_pnl:,.2f}")

data = pd.DataFrame({
    "equity": [2000, 2010, 2025, 2035, 2055]
})

st.line_chart(data)

st.write("Bot online")
