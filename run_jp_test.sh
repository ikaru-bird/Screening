#!/bin/bash

# This script runs the TrendTemplete screening for the top 50 JP stocks.
# It uses the pre-generated CSV data in temp_stock_data_jp/
# and outputs charts to the test_charts_jp/ directory.

set -eu

# Parameters
IN_DIR="temp_stock_data_jp"
OUT_FILE="output_JP/trend_test_results.csv"
CHART_DIR="test_charts_jp"
MA_S=4
MA_M=10
MA_SL=30
MA_L=40
RS_CSV1="_files/RS/rs_industries_jp_test.csv"
RS_CSV2="_files/RS/rs_stocks_jp_test.csv"
TXT_PATH="test_list_jp_top50.txt"

echo "--- Starting TrendTemplete screening test ---"
python isTrend.py \
    "$IN_DIR" \
    "$OUT_FILE" \
    "$CHART_DIR/" \
    "$MA_S" \
    "$MA_M" \
    "$MA_SL" \
    "$MA_L" \
    "$RS_CSV1" \
    "$RS_CSV2" \
    "$TXT_PATH"
echo "--- Test script finished ---"
