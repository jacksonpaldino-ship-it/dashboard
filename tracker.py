# tracker.py

import os
import pandas as pd
from datetime import datetime
from alpaca.trading.client import TradingClient

# =========================================
# CONNECT TO ALPACA
# =========================================

client = TradingClient(
    os.environ["ALPACA_API_KEY"],
    os.environ["ALPACA_SECRET_KEY"],
    paper=False
)

# =========================================
# ACCOUNT INFO
# =========================================

account = client.get_account()

equity = float(account.equity)
cash = float(account.cash)
buying_power = float(account.buying_power)

try:
    last_equity = float(account.last_equity)
except:
    last_equity = equity

daily_pnl = equity - last_equity

# =========================================
# POSITIONS
# =========================================

positions = client.get_all_positions()

total_exposure = 0
positions_data = []

for p in positions:

    market_value = abs(
        float(p.market_value)
    )

    total_exposure += market_value

    positions_data.append({
        "symbol": p.symbol,
        "qty": float(p.qty),
        "market_value": market_value,
        "unrealized_pnl": float(p.unrealized_pl),
        "unrealized_pct": float(p.unrealized_plpc) * 100
    })

exposure_pct = (
    total_exposure / equity
) * 100 if equity > 0 else 0

# =========================================
# SAVE POSITIONS
# =========================================

positions_df = pd.DataFrame(
    positions_data
)

positions_df.to_csv(
    "positions.csv",
    index=False
)

# =========================================
# ORDERS
# =========================================

orders = client.get_orders()

orders_data = []

for o in orders[:200]:

    try:

        orders_data.append({
            "symbol": o.symbol,
            "side": str(o.side),
            "qty": o.qty,
            "status": str(o.status),
            "filled_avg_price": o.filled_avg_price,
            "created_at": o.created_at
        })

    except:
        pass

orders_df = pd.DataFrame(
    orders_data
)

orders_df.to_csv(
    "orders.csv",
    index=False
)

# =========================================
# EQUITY HISTORY
# =========================================

new_row = pd.DataFrame([{
    "timestamp": datetime.now(),
    "equity": equity,
    "cash": cash,
    "buying_power": buying_power,
    "daily_pnl": daily_pnl,
    "exposure_pct": exposure_pct
}])

try:

    history_df = pd.read_csv(
        "equity_history.csv"
    )

    history_df = pd.concat(
        [history_df, new_row],
        ignore_index=True
    )

except:

    history_df = new_row

history_df.to_csv(
    "equity_history.csv",
    index=False
)

# =========================================
# SIGNALS
# =========================================

signals_data = [
    {
        "symbol": "XLE",
        "momentum": 3.2,
        "volatility": 4.1,
        "signal": "BUY"
    },
    {
        "symbol": "NVDA",
        "momentum": 2.1,
        "volatility": 7.2,
        "signal": "BUY"
    },
    {
        "symbol": "SPY",
        "momentum": 1.0,
        "volatility": 1.8,
        "signal": "WATCH"
    }
]

signals_df = pd.DataFrame(
    signals_data
)

signals_df.to_csv(
    "signals.csv",
    index=False
)

# =========================================
# DAILY REPORT
# =========================================

os.makedirs(
    "daily_reports",
    exist_ok=True
)

report = f"""
DAILY REPORT

Date: {datetime.now()}

Equity: ${equity:,.2f}
Cash: ${cash:,.2f}
Buying Power: ${buying_power:,.2f}

Daily PnL: ${daily_pnl:,.2f}

Exposure: {exposure_pct:.2f}%

Open Positions: {len(positions)}

"""

with open(
    f"daily_reports/{datetime.now().date()}.txt",
    "w"
) as f:

    f.write(report)

print("Tracker updated successfully")
