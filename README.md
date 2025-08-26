# Stock Scanner and Backtesting System

A comprehensive Python-based stock analysis and backtesting framework that identifies breakout trading opportunities, analyzes fundamentals, and provides automated email alerts.

## Key Features

- **Advanced Stock Analysis**: Identifies buy signals based on price breakouts and volume spikes
- **Comprehensive Backtesting**: Simulate trading strategies with historical data and performance analytics  
- **Fundamental Analysis**: Generate detailed HTML reports with financial metrics and ratios
- **Automated Alerts**: HTML email notifications for trading signals
- **Multi-Market Support**: Supports stocks from major global exchanges
- **Performance Optimized**: Efficient data processing with pandas vectorization
- **Robust Error Handling**: Comprehensive logging and graceful error management
- **Modern Design**: Clean, responsive email templates and formatted console output

## Project Architecture

```
stockScanner/
├── config.py              # Centralized configuration and constants
├── analyzer.py            # Consolidated stock analysis engine  
├── fetcher.py             # Data retrieval with error handling
├── fund.py                # Fundamental analysis and reporting
├── manager.py             # Main orchestration script
├── notifier.py            # Enhanced email notification system
├── backTesting/           # Backtesting framework
│   ├── analyzer.py        # Lightweight wrapper for backtesting
│   ├── manager.py         # Backtesting execution engine
│   ├── historyFetch.py    # Historical data downloader
│   └── stats.py           # Performance analytics and reporting
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yedidiaSch/stockScanner.git
cd stockScanner

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env
# Edit .env with your email credentials
```

### Configuration

Create a `.env` file with your email settings:
```env
EMAIL_PASSWORD=your_app_password
SENDER_EMAIL=your_email@gmail.com
RECIPIENT_EMAIL=recipient@email.com
```

Create a `tickers.txt` file with stock symbols (one per line):
```
AAPL
MSFT
GOOGL
TSLA
```

## Usage Guide

### 1. Real-time Signal Detection

```bash
python manager.py
```

Analyzes current market data, identifies breakout signals, and sends email alerts with fundamental analysis.

### 2. Historical Data Collection

```bash
python backTesting/historyFetch.py
```

Downloads 5 years of historical data for backtesting.

### 3. Strategy Backtesting

```bash
python backTesting/manager.py
```

Runs comprehensive backtesting with configurable parameters:
- ATR-based stop losses and take profits
- Trailing stop loss management
- Multi-market analysis

### 4. Performance Analytics

```bash
python backTesting/stats.py
```

Generates detailed performance reports:
- Overall portfolio metrics
- Market-by-market analysis  
- Year-over-year performance
- Win rates and risk metrics

## Configuration Options

Key parameters in `config.py`:

```python
# Trading Parameters
DEFAULT_VOLUME_MULTIPLIER = 8.0    # Volume spike threshold
DEFAULT_BREAKOUT_DAYS = 30         # Lookback period for breakouts
DEFAULT_MAX_DAYS_OLD = 5           # Recent signals only

# Backtesting Parameters  
ATR_MULTIPLE = 2.0                 # Stop loss distance
TAKE_PROFIT_MULTIPLE = 4.0         # Take profit distance
EXPIRY_DAYS = 10                   # Maximum hold period
```

## Output Examples

### Email Alert
- **Subject**: "Trading Signals Alert"
- **Content**: Styled HTML with signal list and fundamental reports
- **Metrics**: EPS, P/E ratio, revenue growth, profit margins

### Console Output
```
Portfolio Performance Summary:
==================================================
Total Trades:                    156
Winning Trades:                   89
Win Rate:                      57.1%
Average % per trade:            2.34%
Starting Capital:          ₪50,000
Final Amount:              ₪73,245.67
Total Return:               46.49%
```

## Advanced Features

### Custom Analysis Functions
```python
from analyzer import analyze_stock, get_recent_breakouts

# Analyze last 7 days only
signals = get_recent_breakouts(df, days=7)

# Custom parameters
signals = analyze_stock(
    df,
    volume_multiplier=6.0,
    breakout_days=20,
    max_days_old=3
)
```

### Multi-Market Support
Automatic market detection based on ticker suffixes:
- `.NS` → India
- `.L` → UK  
- `.PA` → France
- `.T` → Japan
- (and many more)

## Performance Optimizations

- **Vectorized Operations**: Uses pandas for efficient data processing
- **Memory Management**: Copies DataFrames to avoid side effects
- **Batch Processing**: Handles multiple tickers efficiently
- **Smart Caching**: Optimized rolling calculations
- **Resource Cleanup**: Proper file and connection management

## Error Handling

- **Input Validation**: Comprehensive parameter checking
- **Graceful Degradation**: Continues processing even if individual stocks fail
- **Detailed Logging**: Structured logging with different severity levels
- **Recovery Mechanisms**: Automatic retries and fallbacks where appropriate

## Dependencies

- **yfinance**: Stock data retrieval
- **pandas**: Data manipulation and analysis
- **numpy**: Numerical computations
- **python-dotenv**: Environment variable management
- **smtplib**: Email functionality (built-in)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your improvements
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This software is for educational and research purposes only. Trading involves risk and past performance does not guarantee future results. Always conduct your own research and consider consulting with financial professionals before making investment decisions.