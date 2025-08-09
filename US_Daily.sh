#!/bin/bash

set -u

# #############################################################
# # Paths for Google Colab Environment
# #############################################################
# BASE_DIR=/content/drive/My\ Drive/Screening/
# STOCK_DIR1=$BASE_DIR/_files/US/
# SCREEN_DATA1=$BASE_DIR/_files/US/input.txt
# OUT_FILE1=$BASE_DIR/output_US/sign.csv
# OUT_DIR=$BASE_DIR/output_US/
# SCRIPT_DIR=$BASE_DIR/_scripts
# RS_CSV1=$BASE_DIR/_files/RS/rs_industries_us.csv
# RS_CSV2=$BASE_DIR/_files/RS/rs_stocks_us.csv


#############################################################
# Paths for Sandbox Environment
#############################################################
BASE_DIR=.
STOCK_DIR1=$BASE_DIR/_files/US/
SCREEN_DATA1=$BASE_DIR/_files/US/input.txt
OUT_FILE1=$BASE_DIR/output_US/sign.csv
OUT_DIR=$BASE_DIR/output_US/
SCRIPT_DIR=$BASE_DIR # Scripts are in the root directory
RS_CSV1=$BASE_DIR/_files/RS/rs_industries_us.csv # Dummy path, file may not exist
RS_CSV2=$BASE_DIR/_files/RS/rs_stocks_us.csv   # Dummy path, file may not exist

# Updated Finviz URL for better pre-filtering
URL='https://finviz.com/screener.ashx?v=152&f=fa_salesqoq_o5,ind_stocksonly,sh_price_o15,ta_averagetruevolume_o100&ft=4&o=-marketcap'

MA_S=10
MA_M=50
MA_SL=150
MA_L=200
INTVAL=1d

# 開始時刻
start_time=`date +%s`

# ディレクトリ構造の準備
mkdir -p $STOCK_DIR1
mkdir -p $OUT_DIR
mkdir -p $BASE_DIR/_files/RS/

# RSデータファイルのプレースホルダーを作成
touch $RS_CSV1
touch $RS_CSV2

# 古い出力ファイルのクリア
rm -f $STOCK_DIR1/*.*

echo "1. Getting ticker list from Finviz..."
python $SCRIPT_DIR/getList_US.py $SCREEN_DATA1 "$URL"

# For testing, limit to first 5 stocks
# head -n 5 $SCREEN_DATA1 > ${SCREEN_DATA1}.tmp && mv ${SCREEN_DATA1}.tmp $SCREEN_DATA1

echo "2. Starting fundamental and technical screening..."
python $SCRIPT_DIR/chkData.py $SCREEN_DATA1 $STOCK_DIR1 $OUT_FILE1 $OUT_DIR $MA_S $MA_M $MA_SL $MA_L $INTVAL $RS_CSV1 $RS_CSV2


# 終了時刻
end_time=`date +%s`

# 処理時間
run_time=$((end_time - start_time))

echo "-- END -- @ " $run_time " sec."
