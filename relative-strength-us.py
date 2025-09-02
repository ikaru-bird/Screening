# --------------------------------------------- #
# 米国株のRelative Strength計算
# --------------------------------------------- #
import sys
import pandas as pd
import RelativeStrength as rs

# --------------------------------------------- #
# 処理開始（メイン）
# --------------------------------------------- #
if __name__ == "__main__":

    if len(sys.argv) < 5:
        print("Usage: python relative-strength-us.py <ticker_list_file> <raw_data_pickle> <rs_result_csv> <rs_sector_csv>")
        sys.exit(1)

    ticker_list_file = sys.argv[1]
    raw_data_pickle = sys.argv[2]
    rs_result_csv = sys.argv[3]
    rs_sector_csv = sys.argv[4]

    print("--- Processing US Stocks ---")

    # Load the ticker list to get metadata (Sector, Industry, etc.)
    columns = ["Ticker", "Company", "Sector", "Industry", "Market Cap", "P/E", "Fwd P/E", "Earnings", "Volume", "Price"]
    try:
        stock_codes = pd.read_csv(ticker_list_file, sep="~", header=None, names=columns)
    except pd.errors.EmptyDataError:
        print(f"Ticker list file {ticker_list_file} is empty, skipping.")
        sys.exit(0)

    # Load the pre-downloaded raw historical data
    try:
        all_history = pd.read_pickle(raw_data_pickle)
    except FileNotFoundError:
        print(f"Raw data file not found: {raw_data_pickle}. Please run the download stage first.")
        sys.exit(1)

    # Execute the calculation
    rs.calc_rs(stock_codes, all_history, rs_result_csv, rs_sector_csv)
    print("--- US Stock Processing Complete ---")
