import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python download_data.py <ticker_list_file> <output_pickle_file>")
        sys.exit(1)

    ticker_list_file = sys.argv[1]
    output_pickle_file = sys.argv[2]

    try:
        tickers_df = pd.read_csv(ticker_list_file, sep="~", header=None)
        tickers = tickers_df[0].unique().tolist()
    except Exception as e:
        print(f"Could not read ticker file {ticker_list_file}: {e}")
        sys.exit(1)

    if not tickers:
        print("No tickers found in the input file.")
        sys.exit(0)

    print(f"Downloading data for {len(tickers)} tickers from {os.path.basename(ticker_list_file)}...")

    start_date = (datetime.now() - timedelta(days=2*365)).strftime("%Y-%m-%d")
    end_date   = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

    all_history = yf.download(
        tickers=tickers,
        start=start_date,
        end=end_date,
        interval="1d",
        auto_adjust=False,
        prepost=False,
        threads=True,
        progress=False
    )

    if not all_history.empty:
        print(f"Download complete. Saving to {output_pickle_file}")
        all_history.to_pickle(output_pickle_file)
    else:
        print("Downloaded data is empty. Nothing to save.")
