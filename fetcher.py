import yfinance as yf
import logging
from typing import Dict, List, Optional
from config import DEFAULT_PERIOD, DEFAULT_INTERVAL

logger = logging.getLogger(__name__)


def fetch_data(tickers: List[str], period: str = DEFAULT_PERIOD) -> Dict:
    """
    Fetches historical stock data for a list of tickers with improved error handling.

    Parameters:
        tickers (List[str]): List of stock tickers to fetch data for.
        period (str): Time period for the data (default from config).

    Returns:
        Dict: A dictionary where keys are tickers and values are DataFrames with stock data.
        
    Raises:
        ValueError: If tickers list is empty or invalid.
        TypeError: If tickers is not a list.
    """
    if not isinstance(tickers, list):
        raise TypeError("tickers must be a list")
    
    if not tickers:
        raise ValueError("tickers list cannot be empty")
    
    # Validate period
    valid_periods = ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"]
    if period not in valid_periods:
        logger.warning(f"Invalid period '{period}', using default '{DEFAULT_PERIOD}'")
        period = DEFAULT_PERIOD
    
    data = {}
    failed_tickers = []
    
    logger.info(f"Fetching data for {len(tickers)} tickers...")
    
    for ticker in tickers:
        if not isinstance(ticker, str) or not ticker.strip():
            logger.warning(f"Invalid ticker: {ticker}, skipping")
            continue
            
        ticker = ticker.strip().upper()
        
        try:
            logger.debug(f"Fetching {ticker}...")
            df = yf.download(
                ticker, 
                period=period, 
                interval=DEFAULT_INTERVAL, 
                auto_adjust=True,
                progress=False,  # Disable progress bar for cleaner logs
                show_errors=False  # Handle errors manually
            )

            # Validate the downloaded data
            if df.empty:
                logger.warning(f"No data returned for {ticker}")
                failed_tickers.append(ticker)
                continue
                
            if "Close" not in df.columns:
                logger.warning(f"Missing 'Close' column for {ticker}")
                failed_tickers.append(ticker)
                continue

            # Reset index for consistency and add ticker validation
            df = df.reset_index()
            
            # Basic data quality checks
            if len(df) < 20:  # Need minimum data for analysis
                logger.warning(f"Insufficient data for {ticker} (only {len(df)} rows)")
                failed_tickers.append(ticker)
                continue
                
            data[ticker] = df
            logger.debug(f"Successfully fetched {len(df)} rows for {ticker}")
            
        except Exception as e:
            logger.error(f"Error fetching data for {ticker}: {e}")
            failed_tickers.append(ticker)
            continue
    
    success_count = len(data)
    total_count = len(tickers)
    
    logger.info(f"Successfully fetched data for {success_count}/{total_count} tickers")
    
    if failed_tickers:
        logger.warning(f"Failed to fetch data for: {', '.join(failed_tickers)}")
    
    return data


def fetch_single_ticker(ticker: str, period: str = DEFAULT_PERIOD) -> Optional[object]:
    """
    Fetch data for a single ticker with error handling.
    
    Args:
        ticker: Stock ticker symbol
        period: Time period for data
        
    Returns:
        DataFrame or None if failed
    """
    result = fetch_data([ticker], period)
    return result.get(ticker)
