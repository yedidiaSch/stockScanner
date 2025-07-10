import yfinance as yf

def fetch_data(tickers, period="6mo"):
    """
    Fetches historical stock data for a list of tickers.

    Parameters:
        tickers (list): List of stock tickers to fetch data for.
        period (str): Time period for the data (default is "6mo").

    Returns:
        dict: A dictionary where keys are tickers and values are DataFrames with stock data.
    """
    data = {}
    for ticker in tickers:
        print(f"Fetching {ticker}...")
        df = yf.download(ticker, period=period, interval="1d", auto_adjust=True)

        # Ensure the DataFrame is valid and contains critical columns
        if not df.empty and "Close" in df.columns:
            df = df.reset_index()  # Reset index for consistency
            data[ticker] = df
        else:
            print(f"No valid data for {ticker}")
    return data
