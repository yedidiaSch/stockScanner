# BackTesting and Stock Analysis Framework

This project provides a comprehensive framework for backtesting trading strategies, analyzing stock data, and generating actionable insights. It includes tools for fetching historical stock data, analyzing trading signals, generating fundamental reports, and sending email alerts for buy signals.

## Features

- **Backtesting**: Simulate trading strategies using historical data and generate performance summaries.
- **Stock Analysis**: Identify buy signals based on breakout and volume criteria.
- **Fundamental Analysis**: Generate detailed HTML reports for stock fundamentals, including EPS, P/E ratio, revenue, and more.
- **Email Notifications**: Automatically send email alerts for identified buy signals.
- **Data Fetching**: Download historical stock data for multiple tickers using Yahoo Finance.

## Project Structure

```
/home/yedidia/github/python/
├── backTesting/
│   ├── stats.py          # Summarizes backtesting results and generates reports.
│   ├── manager.py        # Manages the backtesting process for multiple stocks.
│   ├── historyFetch.py   # Fetches historical stock data for backtesting.
│   ├── analyzer.py       # Analyzes stock data to identify buy signals.
├── fetcher.py            # Fetches historical stock data for analysis.
├── fund.py               # Generates fundamental analysis reports for stocks.
├── manager.py            # Main script for fetching data, analyzing signals, and sending alerts.
├── notifier.py           # Sends email alerts for buy signals.
└── README.md             # Project documentation.
```

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/your-repo-name.git
   cd your-repo-name
   ```

2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root with the following variables:
   ```env
   EMAIL_PASSWORD=your_email_password
   SENDER_EMAIL=your_email@example.com
   RECIPIENT_EMAIL=recipient_email@example.com
   ```

4. Prepare a `tickers.txt` file in the project root with a list of stock tickers (one per line).

## Usage

### 1. Fetch Historical Data
Run the `historyFetch.py` script to download historical stock data:
```bash
python backTesting/historyFetch.py
```

### 2. Backtest Trading Strategies
Run the `manager.py` script to backtest strategies and generate results:
```bash
python backTesting/manager.py
```

### 3. Analyze Buy Signals
Run the `manager.py` script in the root directory to fetch data, analyze signals, and send email alerts:
```bash
python manager.py
```

### 4. Generate Fundamental Reports
Use the `fund.py` script to generate HTML reports for stock fundamentals:
```python
from fund import get_fundamental_report
html_report = get_fundamental_report("AAPL")
print(html_report)
```

## Outputs

- **Backtesting Results**: CSV files summarizing trades and performance metrics.
- **Summary Reports**: Global, market, year, and year-market performance summaries.
- **Email Alerts**: Notifications for buy signals with detailed fundamental reports.

## Example Workflow

1. Add stock tickers to `tickers.txt`:
   ```
   AAPL
   MSFT
   TSLA
   ```

2. Fetch historical data:
   ```bash
   python backTesting/historyFetch.py
   ```

3. Backtest strategies:
   ```bash
   python backTesting/manager.py
   ```

4. Analyze buy signals and send email alerts:
   ```bash
   python manager.py
   ```

## Requirements

- Python 3.7+
- Required Python packages:
  - `pandas`
  - `numpy`
  - `yfinance`
  - `python-dotenv`
  - `smtplib`

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Commit your changes and push to your fork.
4. Submit a pull request with a detailed description of your changes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For questions or feedback, please contact:
- **Name**: Yedidia
- **Email**: your_email@example.com

---

Happy Backtesting! 📈