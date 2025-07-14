import os
from fetcher import fetch_data
from analyzer import analyze_stock
from notifier import send_email_alert
from dotenv import load_dotenv
from fund import get_fundamental_report


def extract_single_ticker_df(df, ticker):
    """
    Extracts a clean DataFrame for a single ticker from a MultiIndex DataFrame.

    Parameters:
        df (DataFrame): MultiIndex DataFrame with stock data.
        ticker (str): Ticker symbol to extract.

    Returns:
        DataFrame: Clean DataFrame with columns ['Date', 'Open', 'High', 'Low', 'Close', 'Volume'].
    """
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

    return df_selected


def main():
    """
    Main function to fetch stock data, analyze for buy signals, and send email alerts.
    """
    # Load environment variables from .env
    load_dotenv()

    email_password = os.getenv("EMAIL_PASSWORD")
    sender_email = os.getenv("SENDER_EMAIL")
    recipient_email = os.getenv("RECIPIENT_EMAIL")

    # Load tickers from a file
    ticker_file = "tickers.txt"
    if not os.path.exists(ticker_file):
        print(f"Ticker file '{ticker_file}' not found.")
        return

    with open(ticker_file) as f:
        tickers = [line.strip() for line in f if line.strip()]

    if not tickers:
        print("No tickers found in file.")
        return

    # Fetch stock data for all tickers
    data = fetch_data(tickers)

    signals = []

    # Analyze each ticker for buy signals
    for ticker in tickers:
        df = data.get(ticker)
        if df is not None:
            df_clean = extract_single_ticker_df(df, ticker)
            signals_list = analyze_stock(
                df_clean,
                volume_multiplier=5.0,         # Adjust volume multiplier as needed
                breakout_days=7,               # Adjust breakout days as needed
                max_days_old=1     # Adjust max days after breakout as needed
            )
            if signals_list:
                signals.append(ticker)

    # Send email if any signals are found
    if signals:
        html_reports = []
        for t in signals:
            html_reports.append(get_fundamental_report(t))

        send_email_alert(
            tickers=signals,
            html_reports=html_reports,
            recipient_email=recipient_email,
            sender_email=sender_email,
            sender_password=email_password
        )
    else:
        print("No signals found.")


if __name__ == "__main__":
    main()
