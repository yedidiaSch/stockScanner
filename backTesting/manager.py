import pandas as pd
from analyzer import analyze_stock
from datetime import datetime, timedelta
import glob
import os

# Function to get market from filename
def get_market_from_filename(filename):
    """
    Extracts the market name from the filename based on its suffix.

    Parameters:
        filename (str): The name of the file.

    Returns:
        str: The market name or "Unknown" if not found.
    """
    suffix_to_market = {
        "NS": "India",
        "DE": "Germany",
        "PA": "France",
        "MI": "Italy",
        "AS": "Netherlands",
        "L": "UK",
        "SS": "China",
        "SZ": "China",
        "T": "Japan",
        "HK": "Hong Kong",
        "TW": "Taiwan",
        "KS": "South Korea",
        "TA": "Tel Aviv",
        "IL": "Israel"
    }

    ticker_part = filename.split("_")[0]

    if "." not in ticker_part:
        return "USA"

    suffix = ticker_part.split(".")[-1]
    market = suffix_to_market.get(suffix.upper(), "Unknown")
    return market

# Find all CSV files in the data folder
csv_files = glob.glob("data/*.csv")

if not csv_files:
    print("⚠️ No CSV files found in data/")
    exit()

# Parameters for backtesting
ATR_MULTIPLE = 2.0
TAKE_PROFIT_MULTIPLE = 4.0
EXPIRY_DAYS = 10

# Define start date for backtest
START_DATE = "2020-07-07"

# Process each CSV file
for file_path in csv_files:
    filename = os.path.basename(file_path)
    market = get_market_from_filename(filename)
    print(f"\n🔹 Processing {filename} (Market: {market})")

    df = pd.read_csv(file_path)

    # Ensure the Date column is valid and sorted
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.dropna(subset=["Date"])
    df = df.sort_values("Date").reset_index(drop=True)

    # Filter data based on the start date
    df = df[df["Date"] >= pd.to_datetime(START_DATE)]

    # Ensure numeric columns are valid
    numeric_columns = ["Adj Close", "Close", "High", "Low", "Open", "Volume"]
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=numeric_columns)

    # Analyze stock for signals
    signals = analyze_stock(df)

    if not signals:
        print("⚠️ No signals found.")
        continue

    # Print signals
    for signal in signals:
        print(f"Date: {signal['date'].strftime('%Y-%m-%d')}, Action: {signal['action']}, Price: {signal['price']:.2f}")

    # Initialize positions
    positions = []
    for signal in signals:
        if signal['action'] == "BUY":
            atr = signal.get("atr")
            if atr is None or pd.isna(atr):
                print(f"⚠️ ATR not valid - skipping trade on {signal['date']}")
                continue

            stop_loss = signal['price'] - (ATR_MULTIPLE * atr)
            take_profit = signal['price'] + (TAKE_PROFIT_MULTIPLE * atr)
            expiry_date = signal['date'] + timedelta(days=EXPIRY_DAYS)

            positions.append({
                "entry_date": signal['date'],
                "entry_price": signal['price'],
                "max_price": signal['price'],
                "stop_loss": stop_loss,
                "take_profit": take_profit,
                "expiry_date": expiry_date,
                "status": "OPEN",
                "exit_date": None,
                "exit_price": None,
                "pct_change": None,
                "atr": atr,
                "market": market
            })

    # Simulate trades
    for idx, row in df.iterrows():
        current_date = row["Date"]
        low = row["Low"]
        high = row["High"]
        for pos in positions:
            if pos["status"] != "OPEN":
                continue

            # Update stop loss based on max price
            if high > pos["max_price"]:
                pos["max_price"] = high
                pos["stop_loss"] = pos["max_price"] - (ATR_MULTIPLE * pos["atr"])

            # Check exit conditions
            if current_date > pos["expiry_date"]:
                pos["status"] = "EXIT TIME"
                pos["exit_date"] = current_date
                pos["exit_price"] = row["Close"]
                pos["pct_change"] = ((pos["exit_price"] - pos["entry_price"]) / pos["entry_price"]) * 100
            elif low <= pos["stop_loss"]:
                pos["status"] = "STOP LOSS"
                pos["exit_date"] = current_date
                pos["exit_price"] = pos["stop_loss"]
                pos["pct_change"] = ((pos["exit_price"] - pos["entry_price"]) / pos["entry_price"]) * 100
            elif high >= pos["take_profit"]:
                pos["status"] = "TAKE PROFIT"
                pos["exit_date"] = current_date
                pos["exit_price"] = pos["take_profit"]
                pos["pct_change"] = ((pos["exit_price"] - pos["entry_price"]) / pos["entry_price"]) * 100

    # Save results to CSV
    results_df = pd.DataFrame(positions)
    out_filename = f"backtest_results_{filename.replace('.csv','')}.csv"
    results_df.to_csv(out_filename, index=False)
    print(f"✅ Results exported to '{out_filename}'")

