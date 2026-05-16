from alpaca.trading.client import TradingClient
import pandas as pd
from datetime import datetime
import os

API_KEY = os.environ["ALPACA_API_KEY"]
SECRET_KEY = os.environ["ALPACA_SECRET_KEY"]

client = TradingClient(
    API_KEY,
    SECRET_KEY,
    paper=False
)

account = client.get_account()

equity = float(account.equity)

new_row = {
    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
    "equity": equity
}

csv_file = "equity_history.csv"

if os.path.exists(csv_file):
    df = pd.read_csv(csv_file)
else:
    df = pd.DataFrame(columns=["timestamp", "equity"])

new_df = pd.concat([
    df,
    pd.DataFrame([new_row])
], ignore_index=True)

new_df.to_csv(csv_file, index=False)

print("Equity history updated")
