"""
Configuration constants for the stock scanner application.
"""

# Trading Parameters
DEFAULT_VOLUME_MULTIPLIER = 8.0
DEFAULT_BREAKOUT_DAYS = 30
DEFAULT_MAX_DAYS_OLD = 5
DEFAULT_ATR_PERIOD = 20
DEFAULT_VOLUME_PERIOD = 20

# Backtesting Parameters
ATR_MULTIPLE = 2.0
TAKE_PROFIT_MULTIPLE = 4.0
EXPIRY_DAYS = 10
START_DATE = "2020-07-07"

# Email Configuration
EMAIL_SMTP_SERVER = "smtp.gmail.com"
EMAIL_SMTP_PORT = 465

# Data Fetching
DEFAULT_PERIOD = "2mo"
DEFAULT_INTERVAL = "1d"

# File Paths
DEFAULT_TICKER_FILE = "tickers.txt"
DATA_DIRECTORY = "data"
BACKTEST_RESULTS_PREFIX = "backtest_results_"

# Market Mappings
MARKET_SUFFIXES = {
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

# Required DataFrame Columns
REQUIRED_COLUMNS = {"High", "Low", "Close", "Volume", "Date"}
NUMERIC_COLUMNS = ["Adj Close", "Close", "High", "Low", "Open", "Volume"]