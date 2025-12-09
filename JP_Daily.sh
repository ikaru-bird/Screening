#!/bin/bash

set -u

# Corrected paths for the sandbox environment
BASE_DIR=.
STOCK_DIR=$BASE_DIR/_files/JP/
SCREEN_DATA0=$BASE_DIR/_files/JP/data_j.xls
SCREEN_DATA1=$BASE_DIR/_files/JP/input.txt
SCREEN_DATA2=$BASE_DIR/_files/indexes/indexes_JP.txt
OUT_FILE1=$BASE_DIR/output_JP/sign.csv
OUT_FILE2=$BASE_DIR/output_JP/trend.csv
OUT_DIR=$BASE_DIR/output_JP/
RS_CSV1=$BASE_DIR/_files/RS/rs_industries_jp.csv
RS_CSV2=$BASE_DIR/_files/RS/rs_stocks_jp.csv
IND_TXT=$BASE_DIR/_files/RS/industries_jp.txt
INTVAL=1d

MA_S=10
MA_M=50
MA_SL=150
MA_L=200

# 開始時刻
start_time=`date +%s`

# 古い出力ファイルのクリア
rm -f $STOCK_DIR/*.*
rm -rf $OUT_DIR

# ディレクトリ構造の準備
mkdir -p $STOCK_DIR
mkdir -p $OUT_DIR
mkdir -p $(dirname $SCREEN_DATA2)
mkdir -p $(dirname $RS_CSV1)
touch $SCREEN_DATA2 # Ensure index file exists

echo "1. Creating Ticker List..."
# スクリーニング＋銘柄リスト作成
python getList_JP.py $SCREEN_DATA0 $SCREEN_DATA1 $STOCK_DIR $IND_TXT

echo "2. Starting Screening..."
# 株価データダウンロード・判定
python chkData.py $SCREEN_DATA1 $STOCK_DIR $OUT_FILE1 $OUT_DIR $MA_S $MA_M $MA_SL $MA_L $INTVAL $RS_CSV1 $RS_CSV2 "Asia/Tokyo"
# python chkData.py $SCREEN_DATA2 $STOCK_DIR $OUT_FILE1 $OUT_DIR $MA_S $MA_M $MA_SL $MA_L $INTVAL $RS_CSV1 $RS_CSV2 "Asia/Tokyo"

# 終了時刻
end_time=`date +%s`

# 処理時間
run_time=$((end_time - start_time))

echo '-- END -- @' $run_time 'sec.'
