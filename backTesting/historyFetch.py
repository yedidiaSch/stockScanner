import yfinance as yf
import pandas as pd
import os

import yfinance as yf
import pandas as pd
import os
import logging
import sys
from typing import List, Optional

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import DATA_DIRECTORY

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def validate_ticker_file(tickers_file: str) -> None:
    """Validate the tickers file exists and is readable."""
    if not os.path.exists(tickers_file):
        raise FileNotFoundError(f"Tickers file '{tickers_file}' not found")
    
    if not os.access(tickers_file, os.R_OK):
        raise PermissionError(f"Cannot read tickers file '{tickers_file}'")


def load_tickers(tickers_file: str) -> List[str]:
    """Load and validate tickers from file."""
    validate_ticker_file(tickers_file)
    
    try:
        with open(tickers_file, "r") as f:
            tickers = [line.strip().upper() for line in f if line.strip() and not line.startswith('#')]
        
        if not tickers:
            raise ValueError("No valid tickers found in file")
        
        logger.info(f"Loaded {len(tickers)} tickers: {tickers}")
        return tickers
        
    except Exception as e:
        logger.error(f"Error reading tickers file: {e}")
        raise


def download_single_ticker(ticker: str, output_dir: str) -> bool:
    """Download data for a single ticker."""
    try:
        logger.info(f"Downloading {ticker}...")
        
        df = yf.download(
            ticker,
            period="5y",
            interval="1d",
            auto_adjust=False,
            progress=False,
            threads=True,
            show_errors=False
        )

        if df.empty:
            logger.warning(f"No data returned for {ticker}")
            return False

        # Validate essential columns
        required_columns = ["Open", "High", "Low", "Close", "Volume"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            logger.warning(f"Missing columns for {ticker}: {missing_columns}")
            return False

        # Reset index to include 'Date' as a column
        df.reset_index(inplace=True)

        # Validate data quality
        if len(df) < 100:  # Need reasonable amount of data
            logger.warning(f"Insufficient data for {ticker} (only {len(df)} rows)")
            return False

        # Save the data to a CSV file
        output_path = os.path.join(output_dir, f"{ticker}_5y.csv")
        df.to_csv(output_path, index=False)
        logger.info(f"Saved {len(df)} rows to {output_path}")
        return True

    except Exception as e:
        logger.error(f"Error downloading {ticker}: {e}")
        return False


def download_data(tickers_file: str, output_dir: str = DATA_DIRECTORY) -> None:
    """
    Downloads historical stock data for a list of tickers and saves them as CSV files.

    Parameters:
        tickers_file (str): Path to the file containing a list of tickers (one per line).
        output_dir (str): Directory where the downloaded data will be saved.
        
    Raises:
        FileNotFoundError: If tickers file doesn't exist.
        ValueError: If no valid tickers found.
    """
    try:
        # Ensure the output directory exists
        os.makedirs(output_dir, exist_ok=True)
        logger.info(f"Output directory: {output_dir}")

        # Load tickers from file
        tickers = load_tickers(tickers_file)

        # Download data for each ticker
        successful_downloads = 0
        failed_downloads = []

        for ticker in tickers:
            success = download_single_ticker(ticker, output_dir)
            if success:
                successful_downloads += 1
            else:
                failed_downloads.append(ticker)

        # Summary
        total_tickers = len(tickers)
        logger.info(f"\n📊 Download Summary:")
        logger.info(f"Total tickers: {total_tickers}")
        logger.info(f"Successful: {successful_downloads}")
        logger.info(f"Failed: {len(failed_downloads)}")
        
        if failed_downloads:
            logger.warning(f"Failed tickers: {', '.join(failed_downloads)}")

    except Exception as e:
        logger.error(f"Error in download_data: {e}")
        raise


if __name__ == "__main__":
    try:
        # Default to tickers.txt in parent directory if it exists
        default_ticker_file = os.path.join("..", "tickers.txt") 
        if not os.path.exists(default_ticker_file):
            default_ticker_file = "tickers.txt"
            
        download_data(default_ticker_file)
        
    except Exception as e:
        logger.error(f"Application failed: {e}")
        sys.exit(1)

