# --------------------------------------------- #
# 米国株のRelative Strength計算・統合版
# --------------------------------------------- #
import sys
import pandas as pd
import RelativeStrength as rs
import argparse
import os
import glob
from datetime import datetime, timedelta
import io

import requests
from bs4 import BeautifulSoup
import time
import re

def get_ticker_list(url, output_file):
    """Fetches ticker list from a Finviz URL, handling pagination."""
    print(f"Fetching tickers from base URL: {url}")
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}

    # Finviz URLs for pagination are of the form &r=21, &r=41, etc.
    # First, get the total number of stocks to determine the number of pages.
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'lxml')

    # Find total number of stocks
    total_stocks_text = soup.find(text=re.compile(r"Total: \d+"))
    if not total_stocks_text:
        print("Could not determine total number of stocks. Processing first page only.")
        total_stocks = 20
    else:
        total_stocks = int(re.search(r'\d+', total_stocks_text).group())

    print(f"Found {total_stocks} total tickers. Fetching all pages...")

    all_tickers_df = pd.DataFrame()

    # Loop through pages. Finviz shows 20 stocks per page.
    for i in range(1, total_stocks, 20):
        paginated_url = f"{url}&r={i}"
        print(f"Fetching page: {paginated_url}")

        response = requests.get(paginated_url, headers=headers)
        soup = BeautifulSoup(response.content, 'lxml')
        table = soup.find('table', {'class': 'screener_table'})

        if table is None:
            print(f"Could not find screener table on page {i}. Stopping.")
            break

        df = pd.read_html(io.StringIO(str(table)), header=0)[0]
        all_tickers_df = pd.concat([all_tickers_df, df], ignore_index=True)
        time.sleep(0.5) # Be respectful to the server

    # Clean up the dataframe
    all_tickers_df.rename(columns={'No.': 'No'}, inplace=True)
    all_tickers_df.drop(columns=['No'], inplace=True)
    all_tickers_df.drop_duplicates(subset=['Ticker'], inplace=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        columns_to_write = ['Ticker', 'Company', 'Sector', 'Industry', 'Market Cap', 'P/E', 'Fwd P/E', 'PEG', 'Volume', 'Price']
        df_cols = [col for col in columns_to_write if col in all_tickers_df.columns]
        for index, row in all_tickers_df[df_cols].iterrows():
            f.write("~".join(map(str, row.values)) + "\n")

    print(f"Saved {len(all_tickers_df)} unique tickers to {output_file}")


def download_raw_data(ticker_list_file, output_pickle_file):
    """Downloads raw historical data for a list of tickers."""
    import yfinance as yf
    try:
        tickers_df = pd.read_csv(ticker_list_file, sep="~", header=None)
        tickers = tickers_df[0].dropna().unique().tolist()
    except Exception as e:
        print(f"Could not read ticker file {ticker_list_file}: {e}", file=sys.stderr)
        return

    if not tickers:
        print("No tickers found in the input file.")
        return

    print(f"Downloading data for {len(tickers)} tickers from {os.path.basename(ticker_list_file)}...")
    start_date = (datetime.now() - timedelta(days=2*365)).strftime("%Y-%m-%d")
    end_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

    all_history = yf.download(
        tickers=tickers, start=start_date, end=end_date, interval="1d",
        auto_adjust=False, prepost=False, threads=True, progress=False
    )

    if not all_history.empty:
        print(f"Download complete. Saving to {output_pickle_file}")
        all_history.to_pickle(output_pickle_file)
    else:
        print("Downloaded data is empty. Nothing to save.")

def combine_raw_data(input_dir, output_pickle_file, pattern):
    """Combines multiple raw data pickle files into one."""
    pickle_files = glob.glob(os.path.join(input_dir, pattern))
    if not pickle_files:
        print(f"No pickle files found in {input_dir} matching pattern {pattern}")
        return

    print(f"Combining {len(pickle_files)} raw data files from {input_dir}...")
    df_list = [pd.read_pickle(f) for f in pickle_files if not pd.read_pickle(f).empty]
    if not df_list:
        print("No data to combine.")
        return

    combined_df = pd.concat(df_list, axis=1)
    if isinstance(combined_df.columns, pd.MultiIndex):
        combined_df = combined_df.loc[:, ~combined_df.columns.duplicated()]

    print(f"Saving combined raw data to {output_pickle_file}")
    combined_df.to_pickle(output_pickle_file)

def run_calculation(ticker_list_file, raw_data_pickle, rs_result_csv, rs_sector_csv):
    """Runs the final RS calculation."""
    print("--- Running Final RS Calculation for US Stocks ---")
    columns = ["Ticker", "Company", "Sector", "Industry", "Market Cap", "P/E", "Fwd P/E", "PEG", "Volume", "Price"]
    try:
        stock_codes = pd.read_csv(ticker_list_file, sep="~", header=None, names=columns)
    except pd.errors.EmptyDataError:
        print(f"Ticker list file {ticker_list_file} is empty, skipping.")
        return

    try:
        all_history = pd.read_pickle(raw_data_pickle)
    except FileNotFoundError:
        print(f"Raw data file not found: {raw_data_pickle}. Please run the download stage first.", file=sys.stderr)
        sys.exit(1)

    rs.calc_rs(stock_codes, all_history, rs_result_csv, rs_sector_csv)
    print("--- US Stock Processing Complete ---")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="US Relative Strength Calculation Script")
    parser.add_argument("--mode", required=True, choices=['get_list', 'download', 'combine', 'calculate'], help="Execution mode")
    args, remaining_argv = parser.parse_known_args()

    if args.mode == 'get_list':
        if len(remaining_argv) != 2:
            sys.exit("Usage for get_list: --mode get_list <url> <output_file>")
        get_ticker_list(remaining_argv[0], remaining_argv[1])

    elif args.mode == 'download':
        if len(remaining_argv) != 2:
            sys.exit("Usage for download: --mode download <ticker_list_file> <output_pickle_file>")
        download_raw_data(remaining_argv[0], remaining_argv[1])

    elif args.mode == 'combine':
        if len(remaining_argv) != 3:
            sys.exit("Usage for combine: --mode combine <input_dir> <output_pickle_file> <pattern>")
        combine_raw_data(remaining_argv[0], remaining_argv[1], remaining_argv[2])

    elif args.mode == 'calculate':
        if len(remaining_argv) != 4:
            sys.exit("Usage for calculate: --mode calculate <ticker_list_file> <raw_data_pickle> <rs_result_csv> <rs_sector_csv>")
        run_calculation(remaining_argv[0], remaining_argv[1], remaining_argv[2], remaining_argv[3])
