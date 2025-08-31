# Googleドライブのライブラリを指定(for Google Colab)
import sys
sys.path.append('/content/drive/MyDrive/Colab Notebooks/my-modules')

import os
import pandas as pd
import yfinance as yf
from classCheckData import CheckData
from classEarningsInfo import EarningsInfo
from datetime import datetime, timedelta
import time

# ==================================================
# OPTIMIZATION STRATEGY:
# 1. Read all tickers from the input file first.
# 2. Download all historical price data in a single batch request.
# 3. In the main loop, perform a fast technical pre-screening (Trend Template).
# 4. Only if the pre-screening passes, perform the slow, network-intensive
#    fundamental analysis for that specific ticker.
# ==================================================

# パラメータの受取り
args = sys.argv
if len(args) < 12:
    print("Usage: python chkData.py <in_path> <out_dir> <out_file> <chart_dir> <ma_short> <ma_mid> <ma_s_long> <ma_long> <dt_interval> <rs_csv1> <rs_csv2> [timezone]")
    sys.exit(1)

in_path     = args[1]
out_dir     = args[2]
out_file    = args[3]
chart_dir   = args[4]
ma_short    = int(args[5])
ma_mid      = int(args[6])
ma_s_long   = int(args[7])
ma_long     = int(args[8])
dt_interval = args[9]
rs_csv1     = args[10]
rs_csv2     = args[11]
timezone_str = args[12] if len(args) > 12 else 'America/New_York'

# STEP 1: Read all tickers from input file
tickers_meta = []
if not os.path.exists(in_path):
    print(f"Input file not found: {in_path}")
    sys.exit(1)

with open(in_path, 'r', encoding='utf-8') as f:
    for line in f.readlines():
        parts = line.strip().split('~')
        if len(parts) > 0 and parts[0]:
            # We only need the symbol for the download, but we'll keep the whole line for later
            tickers_meta.append({'symbol': parts[0], 'roe_str': parts[5]}) # Assuming P/E is at index 5, let's adjust for ROE if available later

if not tickers_meta:
    print("No tickers found in input file.")
    sys.exit(0)

ticker_symbols = [t['symbol'] for t in tickers_meta]
print(f"Found {len(ticker_symbols)} tickers. Downloading all price data in a single batch...")

# STEP 2: Batch download all historical price data
end_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
start_date = (datetime.now() - timedelta(days=2*365)).strftime("%Y-%m-%d")

all_data = yf.download(
    tickers=ticker_symbols,
    start=start_date,
    end=end_date,
    interval="1d" if dt_interval != "1wk" else "1wk",
    auto_adjust=True,
    prepost=False,
    threads=True,
    progress=False # Keep the log clean
)

if all_data.empty:
    print("Could not download any price data from yfinance.")
    sys.exit(1)

print("Price data download complete. Starting analysis...")

# データ処理クラスの作成
ckdt = CheckData(out_file, chart_dir, ma_short, ma_mid, ma_s_long, ma_long, rs_csv1, rs_csv2, in_path, timezone_str)
NG_list = ["COM","AUX","PRN","NUL"]
passed_technicals = 0
passed_fundamentals = 0

# STEP 3 & 4: Main processing loop with sequential screening
for i, ticker_info in enumerate(tickers_meta):
    ticker_str = ticker_info['symbol']
    print(f'{i + 1}/{len(tickers_meta)} ----- {ticker_str} -----')

    # Extract this ticker's data from the batch download
    try:
        # yfinance returns a multi-index column DF. We select one ticker's data.
        symbol_data = all_data.loc[:, pd.IndexSlice[:, [ticker_str]]]
        symbol_data.columns = symbol_data.columns.droplevel(1) # Drop the ticker level from column index
        symbol_data = symbol_data.dropna(how='all')
        if symbol_data.empty:
            # print(f"-> No data for {ticker_str} in downloaded batch. Skipping.")
            continue
    except (KeyError, IndexError):
        # print(f"-> Could not extract data for {ticker_str} from batch. Skipping.")
        continue

    # Use the new setDF method to prepare data without file I/O
    ckdt.setDF(symbol_data, ticker_str)

    # STAGE 1: Fast technical pre-screening
    if ckdt.isTrendTemplete():
        passed_technicals += 1

        # STAGE 2: Slow, on-demand fundamental screening
        try:
            ticker_obj = yf.Ticker(ticker_str)
            # We can't get ROE from the finviz file, so we still need .info
            # This is still a huge win as it's only called for a few tickers
            info = ticker_obj.info
            roe = info.get('returnOnEquity')

            ern_info = EarningsInfo(ticker_obj)
            passed, _ = ern_info.get_fundamental_screening_results(roe)

            if not passed:
                # print(f"-> {ticker_str} did not pass fundamental screening. Skipping.")
                continue

            print(f"{ticker_str} is ::: fundamentaly OK :::")
            passed_fundamentals += 1

            # STAGE 3: Detailed technical analysis for tickers that passed all screens
            ckdt.set_earnings_info(ern_info)

            # The call to isBuySign was removed from isTrendTemplete, so we call it here.
            ckdt.isBuySign()
            ckdt.isGranville()
            ckdt.isGoldernCross()
            ckdt.isON_Minervini()

        except Exception as e:
            # This can happen if yfinance fails for a specific ticker (e.g., delisted)
            print(f"##ERROR## during on-demand data fetch or analysis for {ticker_str}: {e}")
            continue

# Final summary
print("\n--- Analysis Complete ---")
print(f"Total Tickers Analyzed: {len(tickers_meta)}")
print(f"Passed Technical Pre-screen (Trend Template): {passed_technicals}")
print(f"Passed Fundamental Screen: {passed_fundamentals}")

# データ処理クラスの破棄
del ckdt
