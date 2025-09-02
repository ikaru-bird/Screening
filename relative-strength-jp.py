# --------------------------------------------- #
# 日本株のRelative Strength計算・統合版
# --------------------------------------------- #
import sys
import pandas as pd
import numpy as np
import RelativeStrength as rs
import argparse
import os
import glob
from datetime import datetime, timedelta

# Note: The logic from generate_jp_list.py is now integrated here.
import searchIndustryJP as ind

def get_ticker_list(output_file, industry_cache_file):
    """
    Fetches the list of JP stocks from the JPX website,
    enriches it with industry data from yfinance (using a local cache),
    and saves it to a CSV file.
    """
    print("Fetching stock list from JPX...")
    url = 'https://www.jpx.co.jp/markets/statistics-equities/misc/tvdivq0000001vg2-att/data_j.xls'
    stock_codes = pd.read_excel(url, sheet_name='Sheet1')

    stock_codes = stock_codes.rename(columns={'コード': 'Ticker', "市場・商品区分":"SEGMENT", '33業種区分':'Sector', '規模コード':'SIZE'})
    stock_codes['SIZE'] = stock_codes['SIZE'].replace('-', '99').astype(int)

    print("Filtering for Prime and Standard markets...")
    stock_codes = stock_codes.query("SEGMENT == 'プライム（内国株式）' or SEGMENT == 'スタンダード（内国株式）'")

    stock_codes2 = stock_codes.copy()
    stock_codes2['Ticker'] = stock_codes2['Ticker'].apply(lambda x: '{:04}.T'.format(x))
    stock_codes2['Industry'] = np.nan

    try:
        df_tbl = ind.readTable(industry_cache_file)
    except FileNotFoundError:
        df_tbl = pd.DataFrame(columns=['Ticker'])

    missing_industries = []
    print("Checking for industries in local cache...")
    for index, data in stock_codes2.iterrows():
        industry = ind.searchIndustry(df_tbl, data['Ticker'])
        if industry == "-----":
            missing_industries.append((index, data))
        else:
            stock_codes2.loc[index, 'Industry'] = industry

    if missing_industries:
        print(f"Found {len(missing_industries)} tickers with missing industries. Fetching from yfinance...")
        new_industry_lines = []
        for index, data in missing_industries:
            ticker = data['Ticker']
            industry = ind.getTickerIndustry(ticker)
            if industry and str(industry) != 'None':
                stock_codes2.loc[index, 'Industry'] = industry
                new_industry_lines.append(f"{data['Ticker']}~{data['銘柄名']}~{data['Sector']}~{str(industry)}\n")

        if new_industry_lines:
            print(f"Appending {len(new_industry_lines)} new industries to cache file: {industry_cache_file}")
            with open(industry_cache_file, mode='a', encoding='utf-8') as f:
                f.writelines(new_industry_lines)

    stock_codes2['Industry'] = stock_codes2['Industry'].fillna('---')

    stock_codes2.to_csv(output_file, index=False)
    print(f"JP Ticker list generated with {len(stock_codes2)} tickers and saved to {output_file}")


def download_raw_data(ticker_list_file, output_pickle_file):
    """Downloads raw historical data for a list of tickers."""
    import yfinance as yf
    try:
        # For JP list, tickers are in the 'Ticker' column of the CSV
        tickers_df = pd.read_csv(ticker_list_file)
        tickers = tickers_df['Ticker'].dropna().unique().tolist()
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
    print("--- Running Final RS Calculation for JP Stocks ---")
    try:
        stock_codes = pd.read_csv(ticker_list_file)
    except FileNotFoundError:
        print(f"Ticker list file not found: {ticker_list_file}. Please run the download stage first.", file=sys.stderr)
        sys.exit(1)

    try:
        all_history = pd.read_pickle(raw_data_pickle)
    except FileNotFoundError:
        print(f"Raw data file not found: {raw_data_pickle}. Please run the download stage first.", file=sys.stderr)
        sys.exit(1)

    rs.calc_rs(stock_codes, all_history, rs_result_csv, rs_sector_csv)
    print("--- JP Stock Processing Complete ---")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="JP Relative Strength Calculation Script")
    parser.add_argument("--mode", required=True, choices=['get_list', 'download', 'combine', 'calculate'], help="Execution mode")
    args, remaining_argv = parser.parse_known_args()

    if args.mode == 'get_list':
        if len(remaining_argv) != 2:
            sys.exit("Usage for get_list: --mode get_list <output_csv_file> <industry_cache_txt_file>")
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
