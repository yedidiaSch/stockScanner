import os
import logging
from typing import List, Dict, Optional
from fetcher import fetch_data
from analyzer import analyze_stock
from notifier import send_email_alert
from dotenv import load_dotenv
from fund import get_fundamental_report
from config import DEFAULT_TICKER_FILE

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def extract_single_ticker_df(df, ticker: str):
    """
    Extracts a clean DataFrame for a single ticker from a MultiIndex DataFrame.

    Parameters:
        df (DataFrame): MultiIndex DataFrame with stock data.
        ticker (str): Ticker symbol to extract.

    Returns:
        DataFrame: Clean DataFrame with columns ['Date', 'Open', 'High', 'Low', 'Close', 'Volume'].
        
    Raises:
        KeyError: If ticker is not found in DataFrame columns.
        ValueError: If DataFrame structure is invalid.
    """
    if not isinstance(ticker, str) or not ticker.strip():
        raise ValueError("Ticker must be a non-empty string")
        
    try:
        columns_to_select = [
            ('Date', ''),
            ('Open', ticker),
            ('High', ticker),
            ('Low', ticker),
            ('Close', ticker),
            ('Volume', ticker),
        ]

        df_selected = df.loc[:, columns_to_select]
        df_selected.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']

        if df_selected.empty:
            raise ValueError(f"No data found for ticker {ticker}")
            
        return df_selected
        
    except KeyError as e:
        logger.error(f"Ticker {ticker} not found in data: {e}")
        raise
    except Exception as e:
        logger.error(f"Error extracting data for {ticker}: {e}")
        raise


def load_tickers_from_file(ticker_file: str = DEFAULT_TICKER_FILE) -> List[str]:
    """Load and validate tickers from file."""
    if not os.path.exists(ticker_file):
        raise FileNotFoundError(f"Ticker file '{ticker_file}' not found.")

    try:
        with open(ticker_file, 'r') as f:
            tickers = [line.strip().upper() for line in f if line.strip()]
        
        if not tickers:
            raise ValueError("No tickers found in file.")
            
        logger.info(f"Loaded {len(tickers)} tickers from {ticker_file}")
        return tickers
        
    except Exception as e:
        logger.error(f"Error reading ticker file: {e}")
        raise


def validate_email_config(email_password: str, sender_email: str, recipient_email: str) -> None:
    """Validate email configuration."""
    if not all([email_password, sender_email, recipient_email]):
        missing = []
        if not email_password: missing.append("EMAIL_PASSWORD")
        if not sender_email: missing.append("SENDER_EMAIL") 
        if not recipient_email: missing.append("RECIPIENT_EMAIL")
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")


def analyze_tickers_for_signals(tickers: List[str], data: Dict) -> List[str]:
    """Analyze tickers and return those with signals."""
    signals = []
    
    for ticker in tickers:
        try:
            df = data.get(ticker)
            if df is None:
                logger.warning(f"No data available for {ticker}")
                continue
                
            df_clean = extract_single_ticker_df(df, ticker)
            signals_list = analyze_stock(
                df_clean,
                volume_multiplier=4.0,
                breakout_days=12,
                max_days_old=1
            )
            
            if signals_list:
                signals.append(ticker)
                logger.info(f"Signal found for {ticker}")
                
        except Exception as e:
            logger.error(f"Error analyzing {ticker}: {e}")
            continue
    
    return signals


def main():
    """
    Main function to fetch stock data, analyze for buy signals, and send email alerts.
    """
    try:
        # Load environment variables from .env
        load_dotenv()

        email_password = os.getenv("EMAIL_PASSWORD")
        sender_email = os.getenv("SENDER_EMAIL")
        recipient_email = os.getenv("RECIPIENT_EMAIL")

        # Validate email configuration
        validate_email_config(email_password, sender_email, recipient_email)

        # Load tickers from file
        tickers = load_tickers_from_file()

        # Fetch stock data for all tickers
        logger.info("Fetching stock data...")
        data = fetch_data(tickers)

        # Analyze each ticker for buy signals
        logger.info("Analyzing stocks for signals...")
        signals = analyze_tickers_for_signals(tickers, data)

        # Send email if any signals are found
        if signals:
            logger.info(f"Found signals for {len(signals)} stocks: {', '.join(signals)}")
            
            try:
                html_reports = []
                for ticker in signals:
                    try:
                        report = get_fundamental_report(ticker)
                        html_reports.append(report)
                    except Exception as e:
                        logger.warning(f"Could not generate fundamental report for {ticker}: {e}")
                        html_reports.append(f"<p>Report unavailable for {ticker}</p>")

                send_email_alert(
                    tickers=signals,
                    html_reports=html_reports,
                    recipient_email=recipient_email,
                    sender_email=sender_email,
                    sender_password=email_password
                )
                logger.info("Email alert sent successfully")
                
            except Exception as e:
                logger.error(f"Failed to send email alert: {e}")
                raise
        else:
            logger.info("No signals found.")

    except Exception as e:
        logger.error(f"Application error: {e}")
        raise


if __name__ == "__main__":
    main()
