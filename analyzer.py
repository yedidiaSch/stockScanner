import numpy as np
import pandas as pd
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from config import (
    DEFAULT_VOLUME_MULTIPLIER, DEFAULT_BREAKOUT_DAYS, DEFAULT_MAX_DAYS_OLD,
    DEFAULT_ATR_PERIOD, DEFAULT_VOLUME_PERIOD, REQUIRED_COLUMNS
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def validate_dataframe(df: pd.DataFrame) -> None:
    """Validate that DataFrame contains required columns and data."""
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")
    
    if df.empty:
        raise ValueError("DataFrame cannot be empty")
    
    missing_columns = REQUIRED_COLUMNS - set(df.columns)
    if missing_columns:
        raise ValueError(f"DataFrame missing required columns: {missing_columns}")
    
    # Check for numeric columns
    numeric_cols = ["High", "Low", "Close", "Volume"]
    for col in numeric_cols:
        if not pd.api.types.is_numeric_dtype(df[col]):
            raise ValueError(f"Column '{col}' must be numeric")


def calculate_atr(df: pd.DataFrame, period: int = DEFAULT_ATR_PERIOD) -> pd.Series:
    """Calculate Average True Range (ATR) efficiently."""
    high_low = df["High"] - df["Low"]
    high_close = np.abs(df["High"] - df["Close"].shift())
    low_close = np.abs(df["Low"] - df["Close"].shift())
    
    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    return true_range.rolling(window=period, min_periods=1).mean()


def analyze_stock(
    df: pd.DataFrame,
    volume_multiplier: float = DEFAULT_VOLUME_MULTIPLIER,
    breakout_days: int = DEFAULT_BREAKOUT_DAYS,
    max_days_old: Optional[int] = DEFAULT_MAX_DAYS_OLD
) -> List[Dict]:
    """
    Analyze stock data to identify breakout signals with improved error handling and performance.
    
    Parameters:
        df (pd.DataFrame): DataFrame containing stock data with required columns.
        volume_multiplier (float): Multiplier for average volume to identify breakouts.
        breakout_days (int): Number of days to look back for a breakout.
        max_days_old (Optional[int]): Maximum age of signals to include. If None, returns all signals.
    
    Returns:
        List[Dict]: List of signals with date, action, price, and additional metrics.
    
    Raises:
        ValueError: If DataFrame is invalid or missing required columns.
        TypeError: If inputs are of wrong type.
    """
    # Input validation
    validate_dataframe(df)
    
    if volume_multiplier <= 0:
        raise ValueError("volume_multiplier must be positive")
    if breakout_days <= 0:
        raise ValueError("breakout_days must be positive")
    if max_days_old is not None and max_days_old <= 0:
        raise ValueError("max_days_old must be positive or None")
    
    # Work with a copy to avoid modifying original data
    df_work = df.copy().sort_values('Date').reset_index(drop=True)
    
    signals = []
    
    try:
        # Calculate ATR efficiently
        df_work["ATR"] = calculate_atr(df_work)
        
        # Calculate average volume efficiently
        avg_volume = df_work["Volume"].rolling(window=DEFAULT_VOLUME_PERIOD, min_periods=1).mean()
        volume_threshold = avg_volume * volume_multiplier
        
        # Determine cutoff for recent signals
        total_days = len(df_work)
        if max_days_old is not None:
            recent_cutoff_index = max(0, total_days - max_days_old)
        else:
            recent_cutoff_index = 0
        
        # Vectorized calculation of rolling max for breakout detection
        high_rolling_max = df_work["High"].rolling(window=breakout_days, min_periods=breakout_days).max().shift(1)
        
        # Main analysis loop - optimized
        for current_index in range(breakout_days, total_days):
            high_prev = high_rolling_max.iloc[current_index]
            close_today = df_work["Close"].iloc[current_index]
            volume_today = df_work["Volume"].iloc[current_index]
            atr_today = df_work["ATR"].iloc[current_index]
            volume_thresh = volume_threshold.iloc[current_index]
            
            # Skip if any critical value is NaN
            if pd.isna([high_prev, close_today, volume_today, atr_today, volume_thresh]).any():
                continue
            
            # Check breakout conditions
            is_breakout = (close_today > high_prev and volume_today > volume_thresh)
            
            if is_breakout:
                signal_date = df_work["Date"].iloc[current_index]
                logger.info(f"Breakout detected on {signal_date} at price {close_today:.2f}")
                
                # Only append signal if it meets recency criteria
                if current_index >= recent_cutoff_index:
                    signal = {
                        "date": signal_date,
                        "action": "BUY",
                        "price": float(close_today),
                        "atr": float(atr_today),
                        "breakout_high": float(high_prev),
                        "volume": float(volume_today),
                        "avg_volume_threshold": float(volume_thresh),
                        "volume_ratio": float(volume_today / avg_volume.iloc[current_index]) if avg_volume.iloc[current_index] > 0 else 0
                    }
                    signals.append(signal)
                    logger.info(f"Signal added for recent breakout on {signal_date}")
                else:
                    logger.debug(f"Breakout on {signal_date} is older than {max_days_old} days - not added")
    
    except Exception as e:
        logger.error(f"Error during stock analysis: {e}")
        raise
    
    return signals





def get_recent_breakouts(df: pd.DataFrame, days: int = 5) -> List[Dict]:
    """
    Convenience function to get breakouts from the last N days.
    
    Args:
        df: DataFrame with stock data
        days: Number of recent days to analyze
        
    Returns:
        List of signals from recent days
    """
    return analyze_stock(df, max_days_old=days)


def get_today_and_yesterday_breakouts(df: pd.DataFrame) -> List[Dict]:
    """Get breakouts from today and yesterday only."""
    return analyze_stock(df, max_days_old=2)


def get_this_week_breakouts(df: pd.DataFrame) -> List[Dict]:
    """Get breakouts from the last 7 days.""" 
    return analyze_stock(df, max_days_old=7)


def analyze_stock_backtest(
    df: pd.DataFrame, 
    volume_multiplier: float = DEFAULT_VOLUME_MULTIPLIER,
    breakout_days: int = DEFAULT_BREAKOUT_DAYS
) -> List[Dict]:
    """
    Simplified analyze_stock function for backtesting (returns all signals).
    
    This is the equivalent of the backTesting/analyzer.py functionality.
    """
    return analyze_stock(
        df=df,
        volume_multiplier=volume_multiplier, 
        breakout_days=breakout_days,
        max_days_old=None  # Return all signals for backtesting
    )