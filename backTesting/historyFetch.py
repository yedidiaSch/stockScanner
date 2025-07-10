import yfinance as yf
import pandas as pd
import os

def download_data(tickers_file, output_dir="data"):
    """
    Downloads historical stock data for a list of tickers and saves them as CSV files.

    Parameters:
        tickers_file (str): Path to the file containing a list of tickers (one per line).
        output_dir (str): Directory where the downloaded data will be saved (default is "data").
    """
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Read tickers from the file
    with open(tickers_file, "r") as f:
        tickers = [line.strip() for line in f if line.strip()]
    
    print(f"Found {len(tickers)} tickers: {tickers}")

    # Download 5 years of historical data for each ticker
    for ticker in tickers:
        print(f"\nDownloading {ticker}...")
        try:
            df = yf.download(
                ticker,
                period="5y",
                interval="1d",
                auto_adjust=False,
                progress=False,
                threads=True
            )

            if df.empty:
                print(f"  ⚠ No data for {ticker}")
                continue

            # Reset index to include 'Date' as a column
            df.reset_index(inplace=True)

            # Save the data to a CSV file
            output_path = os.path.join(output_dir, f"{ticker}_5y.csv")
            df.to_csv(output_path, index=False)
            print(f"  ✅ Saved to {output_path}")

        except Exception as e:
            print(f"  ❌ Error downloading {ticker}: {e}")

if __name__ == "__main__":
    # Example usage: call with a file named "tickers.txt" in the same folder
    download_data("tickers.txt")

