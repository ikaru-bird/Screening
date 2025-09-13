import yfinance as yf
import pandas as pd
import datetime

def prepare_test_data():
    """
    Reads a list of tickers from 'test_list_jp_top50.txt',
    downloads their weekly historical data for the past 5 years,
    and saves it to CSV files in the 'test_data/' directory.
    """
    input_file = 'test_list_jp_top50.txt'
    output_dir = 'test_data/'

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
        return

    tickers = []
    for line in lines:
        line = line.strip()
        if line:
            # The ticker is the first element, separated by '~'
            ticker = line.split('~')[0]
            if ticker:
                tickers.append(ticker)

    if not tickers:
        print("No tickers found in the input file.")
        return

    print(f"Found {len(tickers)} tickers. Downloading data...")

    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(days=5*365)

    for ticker in tickers:
        try:
            print(f"Downloading data for {ticker}...")
            # Download weekly data
            df = yf.download(ticker, start=start_date, end=end_date, interval="1wk")

            # FIX for tickers that return a MultiIndex column
            if isinstance(df.columns, pd.MultiIndex):
                print(f"Warning: Ticker {ticker} returned MultiIndex columns. Flattening.")
                df.columns = df.columns.droplevel(1)

            if df.empty:
                print(f"No data found for {ticker}, skipping.")
                continue

            # Save to CSV
            output_path = f"{output_dir}{ticker}.csv"
            df.to_csv(output_path)
            print(f"Saved data to {output_path}")

        except Exception as e:
            print(f"Failed to download or save data for {ticker}: {e}")

    print("Data preparation complete.")

if __name__ == '__main__':
    prepare_test_data()
