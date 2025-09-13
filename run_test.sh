#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Define variables
TEST_DATA_DIR="test_data"
CHART_DIR="_files/charts"
TICKER_LIST_FILE="test_list_jp_top50.txt"
TREND_CSV="trend.csv" # Output CSV should not be in the input directory

# Moving Averages and other params from JP_Weekly.sh
MA_S=4
MA_M=10
MA_SL=30
MA_L=40
RS_CSV1="_files/RS/rs_industries_jp_test.csv"
RS_CSV2="_files/RS/rs_stocks_jp_test.csv"

echo "--- Test Start: $(date) ---"

echo "Cleaning up previous run..."
rm -f $TREND_CSV
# Re-create dirs to ensure they are empty
rm -rf $TEST_DATA_DIR
rm -rf $CHART_DIR
mkdir $TEST_DATA_DIR
mkdir $CHART_DIR
echo "Cleanup complete."

# Step 1: Prepare data
# Ensure the python environment has the necessary packages
echo "Installing dependencies..."
# distutils was removed in Python 3.12, but japanize_matplotlib needs it.
# setuptools provides a compatibility layer.
pip install --quiet setuptools
pip install --quiet -r requirements.txt
echo "Dependencies installed."

echo "Running data preparation script (prepare_data.py)..."
python prepare_data.py
echo "Data preparation finished."

# Step 2: Run isTrend.py for screening
echo "Starting Trend screening (isTrend.py)..."
python isTrend.py \
    "$TEST_DATA_DIR" \
    "$TREND_CSV" \
    "$CHART_DIR/" \
    "$MA_S" \
    "$MA_M" \
    "$MA_SL" \
    "$MA_L" \
    "$RS_CSV1" \
    "$RS_CSV2" \
    "$TICKER_LIST_FILE"

echo "--- Test End: $(date) ---"
echo "Test finished. Check '$CHART_DIR' for output images."
