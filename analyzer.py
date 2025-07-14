import numpy as np
import pandas as pd
import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def analyze_stock(
    df: pd.DataFrame,
    volume_multiplier: float = 8.0,
    breakout_days: int = 30,
    max_days_old: int = 5  # Only append signals from last 5 days
) -> list[dict]:
    """
    Analyze stock data to identify breakout signals, but only return signals from recent days.
    The full historical loop runs for proper calculations, but only recent signals are returned.
    
    Parameters:
    df (pd.DataFrame): DataFrame containing stock data with columns 'High', 'Low', 'Close', 'Volume', and 'Date'.
    volume_multiplier (float): Multiplier for average volume to identify breakouts.
    breakout_days (int): Number of days to look back for a breakout.
    max_days_old (int): Maximum age of signals to include (default: 5 days).
    
    Returns:
    list[dict]: List of signals with date, action, price, and ATR (only from recent days).
    """
    required_columns = {"High", "Low", "Close", "Volume", "Date"}
    if not required_columns.issubset(df.columns):
        raise ValueError(f"DataFrame must contain the following columns: {required_columns}")
    
    # Sort by date to ensure proper order
    df = df.sort_values('Date').reset_index(drop=True)
    
    signals = []
    
    # Calculate ATR
    high_low = df["High"] - df["Low"]
    high_close = np.abs(df["High"] - df["Close"].shift())
    low_close = np.abs(df["Low"] - df["Close"].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    df["ATR"] = ranges.max(axis=1).rolling(20).mean()
    
    # Average volume
    avg_volume = df["Volume"].rolling(window=20).mean()
    avg_volume_multiplier = avg_volume * volume_multiplier
    
    def is_breakout(df, current_index, high_prev, avg_volume_multiplier):
        """
        Check if the current day is a breakout.
        """
        close_today = df["Close"].iloc[current_index]
        volume_today = df["Volume"].iloc[current_index]
        
        # Ensure values are not NaN
        if pd.isna(high_prev) or pd.isna(close_today) or pd.isna(volume_today):
            return False
        
        # Check breakout conditions
        return (
            close_today > high_prev and  # Close price exceeds the highest high
            volume_today > avg_volume_multiplier.iloc[current_index]  # Volume exceeds threshold
        )
    
    # Determine the cutoff index for recent signals
    total_days = len(df)
    recent_cutoff_index = max(0, total_days - max_days_old)
    
    # Main loop - runs through ALL history for proper calculations
    for current_index in range(breakout_days, total_days):
        # Calculate the highest high in the breakout_days window
        high_prev = df["High"].iloc[current_index - breakout_days:current_index].max()
        close_today = df["Close"].iloc[current_index]
        volume_today = df["Volume"].iloc[current_index]
        atr_today = df["ATR"].iloc[current_index]
        
        # Skip if any critical value is NaN
        if pd.isna(high_prev) or pd.isna(close_today) or pd.isna(volume_today) or pd.isna(atr_today):
            continue
        
        # Check if today is a breakout
        is_new_breakout = is_breakout(df, current_index, high_prev, avg_volume_multiplier)
        
        if is_new_breakout:
            logger.info(f"Breakout detected on {df['Date'].iloc[current_index]} at price {close_today}")
            
            # Only append signal if it's from the last max_days_old days
            if current_index >= recent_cutoff_index:
                signals.append({
                    "date": df["Date"].iloc[current_index],
                    "action": "BUY",
                    "price": float(close_today),
                    "atr": float(atr_today),
                    "breakout_high": float(high_prev),
                    "volume": float(volume_today),
                    "avg_volume_threshold": float(avg_volume_multiplier.iloc[current_index])
                })
                logger.info(f"Signal added for recent breakout on {df['Date'].iloc[current_index]}")
            else:
                logger.info(f"Breakout on {df['Date'].iloc[current_index]} is older than {max_days_old} days - not added to signals")
    
    return signals





# Example usage functions
def get_recent_breakouts(df: pd.DataFrame, days: int = 5) -> list[dict]:
    """
    Convenience function to get breakouts from the last N days.
    Runs full historical analysis but only returns recent signals.
    """
    return analyze_stock(df, max_days_old=days)


def get_today_and_yesterday_breakouts(df: pd.DataFrame) -> list[dict]:
    """Get breakouts from today and yesterday only."""
    return analyze_stock(df, max_days_old=2)


def get_this_week_breakouts(df: pd.DataFrame) -> list[dict]:
    """Get breakouts from the last 7 days."""
    return analyze_stock(df, max_days_old=7)