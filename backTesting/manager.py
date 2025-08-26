import pandas as pd
import glob
import os
import logging
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Optional

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import consolidated analyzer and config
from analyzer import analyze_stock_backtest
from config import (
    ATR_MULTIPLE, TAKE_PROFIT_MULTIPLE, EXPIRY_DAYS, START_DATE,
    DATA_DIRECTORY, BACKTEST_RESULTS_PREFIX, MARKET_SUFFIXES, NUMERIC_COLUMNS
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_market_from_filename(filename: str) -> str:
    """
    Extracts the market name from the filename based on its suffix.

    Parameters:
        filename (str): The name of the file.

    Returns:
        str: The market name or "Unknown" if not found.
    """
    ticker_part = filename.split("_")[0]

    if "." not in ticker_part:
        return "USA"

    suffix = ticker_part.split(".")[-1]
    return MARKET_SUFFIXES.get(suffix.upper(), "Unknown")


def validate_and_clean_dataframe(df: pd.DataFrame, start_date: str) -> pd.DataFrame:
    """Validate and clean the dataframe for backtesting."""
    try:
        # Ensure the Date column is valid and sorted
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df = df.dropna(subset=["Date"])
        df = df.sort_values("Date").reset_index(drop=True)

        # Filter data based on the start date
        df = df[df["Date"] >= pd.to_datetime(start_date)]

        # Ensure numeric columns are valid
        for col in NUMERIC_COLUMNS:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        
        df = df.dropna(subset=[col for col in NUMERIC_COLUMNS if col in df.columns])
        
        if df.empty:
            raise ValueError("No valid data after cleaning")
            
        return df
    
    except Exception as e:
        logger.error(f"Error cleaning dataframe: {e}")
        raise


def process_single_file(file_path: str) -> Optional[pd.DataFrame]:
    """Process a single CSV file and return results."""
    try:
        filename = os.path.basename(file_path)
        market = get_market_from_filename(filename)
        logger.info(f"Processing {filename} (Market: {market})")

        df = pd.read_csv(file_path)
        df = validate_and_clean_dataframe(df, START_DATE)

        # Analyze stock for signals
        signals = analyze_stock_backtest(df)

        if not signals:
            logger.warning(f"No signals found for {filename}")
            return None

        # Print signals
        for signal in signals:
            logger.info(f"Signal - Date: {signal['date'].strftime('%Y-%m-%d')}, "
                       f"Action: {signal['action']}, Price: {signal['price']:.2f}")

        # Initialize positions
        positions = create_positions_from_signals(signals, market)
        
        # Simulate trades
        simulate_trades(df, positions)

        # Create results DataFrame
        results_df = pd.DataFrame(positions)
        return results_df, filename

    except Exception as e:
        logger.error(f"Error processing {file_path}: {e}")
        return None


def create_positions_from_signals(signals: List[Dict], market: str) -> List[Dict]:
    """Create trading positions from buy signals."""
    positions = []
    
    for signal in signals:
        if signal['action'] == "BUY":
            atr = signal.get("atr")
            if atr is None or pd.isna(atr):
                logger.warning(f"ATR not valid - skipping trade on {signal['date']}")
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
    
    return positions


def simulate_trades(df: pd.DataFrame, positions: List[Dict]) -> None:
    """Simulate trading execution for all positions."""
    for _, row in df.iterrows():
        current_date = row["Date"]
        low = row["Low"] 
        high = row["High"]
        close = row["Close"]
        
        for pos in positions:
            if pos["status"] != "OPEN":
                continue

            # Update stop loss based on max price (trailing stop)
            if high > pos["max_price"]:
                pos["max_price"] = high
                pos["stop_loss"] = pos["max_price"] - (ATR_MULTIPLE * pos["atr"])

            # Check exit conditions in order of priority
            if current_date > pos["expiry_date"]:
                close_position(pos, "EXIT TIME", current_date, close)
            elif low <= pos["stop_loss"]:
                close_position(pos, "STOP LOSS", current_date, pos["stop_loss"])
            elif high >= pos["take_profit"]:
                close_position(pos, "TAKE PROFIT", current_date, pos["take_profit"])


def close_position(position: Dict, status: str, exit_date, exit_price: float) -> None:
    """Close a trading position and calculate returns."""
    position["status"] = status
    position["exit_date"] = exit_date
    position["exit_price"] = exit_price
    position["pct_change"] = ((exit_price - position["entry_price"]) / position["entry_price"]) * 100


def main():
    """Main backtesting execution function."""
    # Find all CSV files in the data folder
    csv_files = glob.glob(f"{DATA_DIRECTORY}/*.csv")

    if not csv_files:
        logger.error(f"No CSV files found in {DATA_DIRECTORY}/")
        return

    logger.info(f"Found {len(csv_files)} files to process")

    # Process each CSV file
    for file_path in csv_files:
        result = process_single_file(file_path)
        
        if result is not None:
            results_df, filename = result
            # Save results to CSV
            out_filename = f"{BACKTEST_RESULTS_PREFIX}{filename.replace('.csv','')}.csv"
            results_df.to_csv(out_filename, index=False)
            logger.info(f"Results exported to '{out_filename}'")


if __name__ == "__main__":
    main()

