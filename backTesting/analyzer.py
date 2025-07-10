import numpy as np
import pandas as pd

def analyze_stock(df, volume_multiplier=8.0, breakout_days=30):
    """
    Analyzes stock data to identify buy signals based on breakout and volume criteria.

    Parameters:
        df (DataFrame): Stock data with columns ['High', 'Low', 'Close', 'Volume', 'Date'].
        volume_multiplier (float): Multiplier for average volume to identify significant volume spikes.
        breakout_days (int): Number of days to look back for breakout levels.

    Returns:
        list: A list of buy signals, each containing date, action, price, and ATR.
    """
    signals = []

    # Calculate Average True Range (ATR)
    high_low = df["High"] - df["Low"]
    high_close = np.abs(df["High"] - df["Close"].shift())
    low_close = np.abs(df["Low"] - df["Close"].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    df["ATR"] = ranges.max(axis=1).rolling(20).mean()

    # Calculate 20-day average volume
    avg_volume = df["Volume"].rolling(window=20).mean()

    # Iterate through each day to identify buy signals
    for i in range(breakout_days, len(df)):
        high_prev = df["High"].iloc[i - breakout_days:i].max()
        close_today = df["Close"].iloc[i]
        volume_today = df["Volume"].iloc[i]
        atr_today = df["ATR"].iloc[i]

        # Check breakout and volume conditions
        if (
            close_today > high_prev
            and volume_today > avg_volume.iloc[i] * volume_multiplier
            and not pd.isna(atr_today)
        ):
            signals.append({
                "date": df["Date"].iloc[i],
                "action": "BUY",
                "price": float(close_today),
                "atr": float(atr_today)
            })

    return signals
