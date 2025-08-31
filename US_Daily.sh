#!/bin/bash

set -u

#############################################################
# Paths for Sandbox Environment
#############################################################
BASE_DIR=.
STOCK_DIR1=/content/_files/US/
STOCK_DIR2=/content/_files/US-INDEX/
SCREEN_DATA1=/content/_files/US/input.txt
SCREEN_DATA2=$BASE_DIR/_files/indexes/indexes_US.txt
OUT_FILE1=$BASE_DIR/output_US/sign.csv
OUT_FILE2=$BASE_DIR/output_US/trend.csv
OUT_DIR=$BASE_DIR/output_US/
SCRIPT_DIR=$BASE_DIR/_scripts
RS_CSV1=$BASE_DIR/_files/RS/rs_industries_us.csv
RS_CSV2=$BASE_DIR/_files/RS/rs_stocks_us.csv

# Updated Finviz URL for better pre-filtering
URL='https://finviz.com/screener.ashx?v=152&f=fa_epsqoq_o10,fa_epsyoy_o10,ind_stocksonly,sh_price_o10&ft=2&o=-marketcap&c=0,1,2,3,4,6,7,8,65,67,68'

MA_S=10
MA_M=50
MA_SL=150
MA_L=200
INTVAL=1d

# 開始時刻
start_time=`date +%s`

# ディレクトリの移動
cd '/content/drive/MyDrive/Screening/'

# 古い出力ファイルのクリア
rm -f $STOCK_DIR1/*.*
rm -f $STOCK_DIR2/*.*
rm -rf $OUT_DIR

# ディレクトリ構造の準備
mkdir -p $STOCK_DIR1
mkdir -p $STOCK_DIR2
mkdir -p $OUT_DIR
mkdir -p $BASE_DIR/_files/RS/

# RSデータファイルのプレースホルダーを作成
touch $RS_CSV1
touch $RS_CSV2

echo "1. Getting ticker list from Finviz..."
python $SCRIPT_DIR/getList_US.py $SCREEN_DATA1 "$URL"

echo "2. Starting fundamental and technical screening..."
python $SCRIPT_DIR/chkData.py $SCREEN_DATA1 $STOCK_DIR1 $OUT_FILE1 $OUT_DIR $MA_S $MA_M $MA_SL $MA_L $INTVAL $RS_CSV1 $RS_CSV2
python $SCRIPT_DIR/chkData.py $SCREEN_DATA2 $STOCK_DIR2 $OUT_FILE1 $OUT_DIR $MA_S $MA_M $MA_SL $MA_L $INTVAL $RS_CSV1 $RS_CSV2

echo "3. Starting TrendTemplete screening...(indexes only)"
python $SCRIPT_DIR/isTrend.py $STOCK_DIR2 $OUT_FILE2 $OUT_DIR/Trend- $MA_S $MA_M $MA_SL $MA_L $RS_CSV1 $RS_CSV2 $SCREEN_DATA2

# 終了時刻
end_time=`date +%s`

# 処理時間
run_time=$((end_time - start_time))

echo "-- END -- @ " $run_time " sec."
