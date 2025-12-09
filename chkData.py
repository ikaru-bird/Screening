import sys
import os
import pandas as pd
import yfinance as yf
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
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
# 5. Crucially, save the price data for each ticker to a CSV file so that
#    downstream scripts like isTrend.py can function correctly.
# ==================================================

# パラメータの受取り
args = sys.argv
if len(args) < 12:
    print("Usage: python chkData.py <in_path> <stock_dir> <out_file> <chart_dir> <ma_short> <ma_mid> <ma_s_long> <ma_long> <dt_interval> <rs_csv1> <rs_csv2> [timezone]")
    sys.exit(1)

in_path     = args[1]
stock_dir   = args[2] # This is the directory for individual CSVs
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
            tickers_meta.append({'symbol': parts[0]})

if not tickers_meta:
    print("No tickers found in input file.")
    sys.exit(0)

ticker_symbols = [t['symbol'] for t in tickers_meta]

# STEP 2: Batch download all historical price data in chunks
chunk_size = 200
all_data_list = []
ticker_chunks = [ticker_symbols[i:i + chunk_size] for i in range(0, len(ticker_symbols), chunk_size)]

print(f"Found {len(ticker_symbols)} tickers. Downloading data in {len(ticker_chunks)} chunks of up to {chunk_size} tickers each.")

end_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
start_date = (datetime.now() - timedelta(days=2*365)).strftime("%Y-%m-%d")

for i, chunk in enumerate(ticker_chunks):
    print(f"Downloading chunk {i + 1}/{len(ticker_chunks)}...")
    try:
        data = yf.download(
            tickers=chunk,
            start=start_date,
            end=end_date,
            interval="1d" if dt_interval != "1wk" else "1wk",
            auto_adjust=True,
            prepost=False,
            threads=True,
            progress=False
        )
        if not data.empty:
            all_data_list.append(data)
        else:
            print(f"Warning: No data returned for chunk {i + 1}.")

        # Wait for 5 seconds before the next chunk to avoid rate limiting
        if i < len(ticker_chunks) - 1:
            time.sleep(5)

    except Exception as e:
        print(f"Error downloading chunk {i + 1}: {e}")
        continue

if not all_data_list:
    print("Could not download any price data from yfinance after all chunks.")
    sys.exit(1)

# Combine all downloaded data chunks
all_data = pd.concat(all_data_list, axis=1)

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
        symbol_data = all_data.loc[:, pd.IndexSlice[:, [ticker_str]]]
        symbol_data.columns = symbol_data.columns.droplevel(1)
        symbol_data = symbol_data.dropna(how='all')
        if symbol_data.empty:
            continue
    except (KeyError, IndexError):
        continue

    # STEP 5: Save individual CSV for downstream scripts (isTrend.py)
    if ticker_str in NG_list:
        fileName = os.path.join(stock_dir, f"{ticker_str}-X.csv")
    else:
        fileName = os.path.join(stock_dir, f"{ticker_str}.csv")
    symbol_data.to_csv(fileName, header=True, index=True)

    # Use the new setDF method to prepare data without file I/O
    ckdt.setDF(symbol_data, ticker_str)

    # STAGE 1: Fast technical pre-screening
    if ckdt.isTrendTemplete():
        passed_technicals += 1

        # STAGE 2 & 3: Create earnings info object, then perform detailed technical analysis.
        # The fundamental check is now inside the writeFlles method in classCheckData.
        try:
            ticker_obj = yf.Ticker(ticker_str)
            ern_info = EarningsInfo(ticker_obj)
            ckdt.set_earnings_info(ern_info) # Set ern_info before technical checks

            # These methods will call writeFlles internally, which now performs the fundamental check.
            ckdt.isBuySign()
            ckdt.isGranville()
            ckdt.isGoldernCross()
            ckdt.isON_Minervini()

        except Exception as e:
            print(f"##ERROR## during on-demand data fetch or analysis for {ticker_str}: {e}")
            continue

# Final summary
print("\n--- Analysis Complete ---")
print(f"Total Tickers Analyzed: {len(tickers_meta)}")
print(f"Passed Technical Pre-screen (Trend Template): {passed_technicals}")
# print(f"Passed Fundamental Screen: {passed_fundamentals}")

# データ処理クラスの破棄
del ckdt
