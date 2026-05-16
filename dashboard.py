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

/* SIDEBAR TITLE */
.sidebar-title {
    color: #72FF5B;
    font-size: 2rem;
    font-weight: 800;
    line-height: 1.2;
    margin-bottom: 2rem;
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
# LOAD EQUITY HISTORY
# =========================================

try:

    history_df = pd.read_csv(
        "equity_history.csv"
    )

except:

    history_df = pd.DataFrame({
        "timestamp": [],
        "equity": []
    })

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

page = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Overview",
        "📦 Positions",
        "🧾 Orders",
        "📈 Performance",
        "📊 Analytics",
        "⚙ Settings"
    ]
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
# OVERVIEW PAGE
# =========================================

if page == "🏠 Overview":

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

    st.markdown(
        '<div class="section-header">📈 Equity Curve</div>',
        unsafe_allow_html=True
    )

    if len(history_df) > 0:

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=history_df["timestamp"],
                y=history_df["equity"],
                mode="lines",
                line=dict(
                    color="#72FF5B",
                    width=4
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

    else:

        st.warning(
            "No equity history data yet"
        )

# =========================================
# POSITIONS PAGE
# =========================================

elif page == "📦 Positions":

    st.markdown(
        '<div class="section-header">📦 Open Positions</div>',
        unsafe_allow_html=True
    )

    positions = client.get_all_positions()

    if positions:

        data = []

        total_exposure = 0

        for p in positions:

            market_value = float(
                p.market_value
            )

            total_exposure += abs(
                market_value
            )

            data.append({
                "Symbol": p.symbol,
                "Qty": p.qty,
                "Avg Entry": p.avg_entry_price,
                "Current Price": p.current_price,
                "Market Value": p.market_value,
                "PnL": p.unrealized_pl
            })

        df = pd.DataFrame(data)

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

        exposure_pct = (
            total_exposure / equity
        ) * 100 if equity > 0 else 0

        st.metric(
            "Portfolio Exposure",
            f"{exposure_pct:.1f}%"
        )

    else:
        st.info("No open positions")

# =========================================
# ORDERS PAGE
# =========================================

elif page == "🧾 Orders":

    st.markdown(
        '<div class="section-header">🧾 Recent Orders</div>',
        unsafe_allow_html=True
    )

    try:

        orders = client.get_orders()

        order_data = []

        for o in orders[:50]:

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

        st.warning(
            "Could not load orders"
        )

        st.write(e)

# =========================================
# PERFORMANCE PAGE
# =========================================

elif page == "📈 Performance":

    st.markdown(
        '<div class="section-header">📈 Performance Stats</div>',
        unsafe_allow_html=True
    )

    p1, p2, p3, p4 = st.columns(4)

    p1.metric(
        "Portfolio Value",
        f"${equity:,.2f}"
    )

    p2.metric(
        "Today's Return",
        f"{daily_pnl_pct:.2f}%"
    )

    p3.metric(
        "Buying Power",
        f"${buying_power:,.2f}"
    )

    p4.metric(
        "Account Status",
        "ACTIVE"
    )

    st.markdown("<br>", unsafe_allow_html=True)

    if len(history_df) > 0:

        start_equity = history_df[
            "equity"
        ].iloc[0]

        current_equity = history_df[
            "equity"
        ].iloc[-1]

        total_return = (
            (
                current_equity
                - start_equity
            )
            / start_equity
        ) * 100

        peak_equity = history_df[
            "equity"
        ].max()

        drawdown_pct = (
            (
                peak_equity
                - current_equity
            )
            / peak_equity
        ) * 100

        d1, d2 = st.columns(2)

        d1.metric(
            "Total Return",
            f"{total_return:.2f}%"
        )

        d2.metric(
            "Drawdown",
            f"{drawdown_pct:.2f}%"
        )

# =========================================
# ANALYTICS PAGE
# =========================================

elif page == "📊 Analytics":

    st.markdown(
        '<div class="section-header">📊 Advanced Analytics</div>',
        unsafe_allow_html=True
    )

    try:

        orders = client.get_orders()
        positions = client.get_all_positions()

        completed_trades = []
        buy_prices = {}

        for o in orders:

            try:

                symbol = o.symbol
                side = str(o.side).lower()
                qty = float(o.qty)

                try:
                    filled_price = float(
                        o.filled_avg_price
                    )
                except:
                    continue

                if side == "buy":

                    buy_prices[symbol] = (
                        filled_price
                    )

                elif side == "sell":

                    if symbol in buy_prices:

                        entry = buy_prices[
                            symbol
                        ]

                        exit_price = (
                            filled_price
                        )

                        pnl = (
                            exit_price
                            - entry
                        ) * qty

                        pnl_pct = (
                            (
                                exit_price
                                - entry
                            )
                            / entry
                        ) * 100

                        completed_trades.append({
                            "symbol": symbol,
                            "entry": entry,
                            "exit": exit_price,
                            "qty": qty,
                            "pnl": pnl,
                            "pnl_pct": pnl_pct
                        })

            except:
                pass

        trades_df = pd.DataFrame(
            completed_trades
        )

        if len(trades_df) > 0:

            winning_trades = trades_df[
                trades_df["pnl"] > 0
            ]

            losing_trades = trades_df[
                trades_df["pnl"] <= 0
            ]

            total_trades = len(
                trades_df
            )

            win_rate = (
                len(winning_trades)
                / total_trades
            ) * 100

            avg_win = winning_trades[
                "pnl"
            ].mean()

            avg_loss = losing_trades[
                "pnl"
            ].mean()

            gross_profit = winning_trades[
                "pnl"
            ].sum()

            gross_loss = abs(
                losing_trades[
                    "pnl"
                ].sum()
            )

            if gross_loss > 0:
                profit_factor = (
                    gross_profit
                    / gross_loss
                )
            else:
                profit_factor = 0

            expectancy = (
                (
                    win_rate / 100
                ) * avg_win
            ) + (
                (
                    (100 - win_rate)
                    / 100
                ) * avg_loss
            )

            c1, c2, c3, c4, c5 = st.columns(5)

            c1.metric(
                "Win Rate",
                f"{win_rate:.1f}%"
            )

            c2.metric(
                "Avg Win",
                f"${avg_win:,.2f}"
            )

            c3.metric(
                "Avg Loss",
                f"${avg_loss:,.2f}"
            )

            c4.metric(
                "Profit Factor",
                f"{profit_factor:.2f}"
            )

            c5.metric(
                "Expectancy",
                f"${expectancy:,.2f}"
            )

            st.markdown(
                "<br>",
                unsafe_allow_html=True
            )

            symbol_stats = {}

            for trade in completed_trades:

                symbol = trade["symbol"]
                pnl = trade["pnl"]

                if symbol not in symbol_stats:
                    symbol_stats[symbol] = 0

                symbol_stats[symbol] += pnl

            if symbol_stats:

                best_symbol = max(
                    symbol_stats,
                    key=symbol_stats.get
                )

                worst_symbol = min(
                    symbol_stats,
                    key=symbol_stats.get
                )

                best_symbol_pnl = (
                    symbol_stats[
                        best_symbol
                    ]
                )

                worst_symbol_pnl = (
                    symbol_stats[
                        worst_symbol
                    ]
                )

                d1, d2 = st.columns(2)

                d1.metric(
                    f"Best Symbol: {best_symbol}",
                    f"${best_symbol_pnl:,.2f}"
                )

                d2.metric(
                    f"Worst Symbol: {worst_symbol}",
                    f"${worst_symbol_pnl:,.2f}"
                )

        total_exposure = 0

        for p in positions:

            total_exposure += abs(
                float(p.market_value)
            )

        exposure_pct = (
            total_exposure / equity
        ) * 100 if equity > 0 else 0

        if exposure_pct > 70:

            st.error(
                "⚠ WARNING: Exposure above 70%"
            )

        if len(history_df) > 0:

            history_df[
                "rolling_max"
            ] = history_df[
                "equity"
            ].cummax()

            history_df[
                "drawdown"
            ] = (
                history_df["equity"]
                - history_df["rolling_max"]
            ) / history_df[
                "rolling_max"
            ] * 100

            fig_dd = go.Figure()

            fig_dd.add_trace(
                go.Scatter(
                    x=history_df[
                        "timestamp"
                    ],
                    y=history_df[
                        "drawdown"
                    ],
                    fill="tozeroy",
                    line=dict(
                        color="#FF4B4B",
                        width=3
                    )
                )
            )

            fig_dd.update_layout(
                template="plotly_dark",
                paper_bgcolor="#040816",
                plot_bgcolor="#040816",
                title="Drawdown",
                font_color="white",
                height=350
            )

            st.plotly_chart(
                fig_dd,
                use_container_width=True
            )

        st.markdown(
            '<div class="section-header">📓 Trade Journal</div>',
            unsafe_allow_html=True
        )

        journal_data = []

        for trade in completed_trades:

            journal_data.append({
                "Symbol": trade["symbol"],
                "Entry": round(
                    trade["entry"], 2
                ),
                "Exit": round(
                    trade["exit"], 2
                ),
                "PnL": round(
                    trade["pnl"], 2
                ),
                "PnL %": round(
                    trade["pnl_pct"], 2
                )
            })

        journal_df = pd.DataFrame(
            journal_data
        )

        st.dataframe(
            journal_df,
            use_container_width=True,
            hide_index=True
        )

    except Exception as e:

        st.warning(
            "Analytics unavailable"
        )

        st.write(e)

# =========================================
# SETTINGS PAGE
# =========================================

elif page == "⚙ Settings":

    st.markdown(
        '<div class="section-header">⚙ Settings</div>',
        unsafe_allow_html=True
    )

    st.write(
        "Connected to Alpaca Live Account"
    )

    st.write(
        f"Last Updated: {datetime.now().strftime('%b %d, %Y %I:%M %p')}"
    )

    if st.button(
        "Refresh Dashboard"
    ):
        st.rerun()

# =========================================
# FOOTER
# =========================================

st.markdown(
    "<br>",
    unsafe_allow_html=True
)

st.success(
    "Dashboard Connected Successfully"
)
