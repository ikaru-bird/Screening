#!/bin/bash

set -u

# --- Configuration ---
BASE_DIR=.
SCRIPT_DIR=$BASE_DIR
INPUT_DIR=$BASE_DIR/_files/RS
OUTPUT_DIR=$BASE_DIR/_files/RS
CHUNK_DIR=$INPUT_DIR/chunks_raw_tickers
RAW_DATA_DIR=$INPUT_DIR/raw_data_pkl
COMBINED_DATA_DIR=$INPUT_DIR/combined_raw_data

US_TICKER_LIST=$INPUT_DIR/input_us_tickers.txt
JP_TICKER_LIST=$INPUT_DIR/jp_full_list.csv
IND_TXT_CACHE=$INPUT_DIR/industries_jp.txt

URL_US_TICKERS="https://finviz.com/screener.ashx?v=152&f=cap_smallover,ind_stocksonly,sh_price_o7&o=-marketcap&c=0,1,2,3,4,6,7,8,65,67,68"

CHUNK_SIZE=100
WAIT_SECONDS=5

# --- Cleanup and Setup ---
echo "--- Initializing directories ---"
rm -rf $CHUNK_DIR $RAW_DATA_DIR $COMBINED_DATA_DIR
mkdir -p $CHUNK_DIR $RAW_DATA_DIR $COMBINED_DATA_DIR
touch "$IND_TXT_CACHE"
echo

# --- Main Logic ---
start_time=$(date +%s)

# --- STAGE 1: Generate Master Ticker Lists ---
echo "--- Stage 1: Generating Master Ticker Lists ---"
python3 "$SCRIPT_DIR/getList_US.py" "$US_TICKER_LIST" "$URL_US_TICKERS"
python3 "$SCRIPT_DIR/generate_jp_list.py" "$JP_TICKER_LIST" "$IND_TXT_CACHE"
echo "Ticker list generation complete."
echo

# --- STAGE 2: Download Raw Data in Chunks ---
echo "--- Stage 2: Downloading Raw Stock Data in Chunks ---"
# US Chunks
split -l $CHUNK_SIZE "$US_TICKER_LIST" "$CHUNK_DIR/us_tickers_"
us_chunks=($CHUNK_DIR/us_tickers_*)
echo "Split US tickers into ${#us_chunks[@]} chunks."
for file in "${us_chunks[@]}"; do
    fname=$(basename "$file")
    echo "Downloading US chunk: $fname..."
    python3 "$SCRIPT_DIR/download_data.py" "$file" "$RAW_DATA_DIR/us_raw_$fname.pkl"
    echo "Waiting for $WAIT_SECONDS seconds..."
    sleep $WAIT_SECONDS
done

# JP Chunks (temporary file to pass tickers without header)
tmp_jp_tickers="$CHUNK_DIR/jp_tickers_only.txt"
tail -n +2 "$JP_TICKER_LIST" | cut -d, -f1 > "$tmp_jp_tickers"
split -l $CHUNK_SIZE "$tmp_jp_tickers" "$CHUNK_DIR/jp_tickers_"
rm "$tmp_jp_tickers"
jp_chunks=($CHUNK_DIR/jp_tickers_*)
echo "Split JP tickers into ${#jp_chunks[@]} chunks."
for file in "${jp_chunks[@]}"; do
    fname=$(basename "$file")
    echo "Downloading JP chunk: $fname..."
    python3 "$SCRIPT_DIR/download_data.py" "$file" "$RAW_DATA_DIR/jp_raw_$fname.pkl"
    echo "Waiting for $WAIT_SECONDS seconds..."
    sleep $WAIT_SECONDS
done
echo "Raw data download complete."
echo

# --- STAGE 3: Combine Raw Data ---
echo "--- Stage 3: Combining Raw Data Files ---"
python3 "$SCRIPT_DIR/combine_raw_data.py" "$RAW_DATA_DIR" "$COMBINED_DATA_DIR/us_raw_data.pkl" --pattern="us_raw_*.pkl"
python3 "$SCRIPT_DIR/combine_raw_data.py" "$RAW_DATA_DIR" "$COMBINED_DATA_DIR/jp_raw_data.pkl" --pattern="jp_raw_*.pkl"
echo "Raw data combination complete."
echo

# --- STAGE 4: Calculate RS Values (Single Run) ---
echo "--- Stage 4: Calculating RS Values ---"
python3 "$SCRIPT_DIR/relative-strength-us.py" \
    "$US_TICKER_LIST" \
    "$COMBINED_DATA_DIR/us_raw_data.pkl" \
    "$OUTPUT_DIR/rs_stocks_us.csv" \
    "$OUTPUT_DIR/rs_industries_us.csv"

python3 "$SCRIPT_DIR/relative-strength-jp.py" \
    "$JP_TICKER_LIST" \
    "$COMBINED_DATA_DIR/jp_raw_data.pkl" \
    "$OUTPUT_DIR/rs_stocks_jp.csv" \
    "$OUTPUT_DIR/rs_industries_jp.csv"
echo "RS calculation complete."
echo

# --- STAGE 5: Create RS Charts ---
echo "--- Stage 5: Creating RS Charts ---"
python3 "$SCRIPT_DIR/SectorRS_US.py" "$OUTPUT_DIR/rs_industries_us.csv" "$OUTPUT_DIR/rs_industries_us.png"
python3 "$SCRIPT_DIR/SectorRS_JP.py" "$OUTPUT_DIR/rs_industries_jp.csv" "$OUTPUT_DIR/rs_industries_jp.png"
echo "Chart generation complete."
echo

# --- Finalization ---
end_time=$(date +%s)
run_time=$((end_time - start_time))
echo "--- ALL DONE ---"
echo "Total processing time: $run_time seconds."
