#!/bin/bash

set -u

# Corrected paths for the sandbox environment
BASE_DIR=.
STOCK_DIR=$BASE_DIR/_files/US/
SCREEN_DATA1=$BASE_DIR/_files/US/input.txt
SCREEN_DATA2=$BASE_DIR/_files/indexes/indexes_US.txt
OUT_FILE1=$BASE_DIR/output_US/sign.csv
OUT_FILE2=$BASE_DIR/output_US/trend.csv
OUT_DIR=$BASE_DIR/output_US/
RS_CSV1=$BASE_DIR/_files/RS/rs_industries_us.csv
RS_CSV2=$BASE_DIR/_files/RS/rs_stocks_us.csv
INTVAL=1wk
SCRIPT_DIR=$BASE_DIR

# This is the correct URL provided by the user
URL='https://finviz.com/screener.ashx?v=152&f=fa_epsqoq_o10,fa_epsyoy_o10,ind_stocksonly,sh_price_o10&ft=2&o=-marketcap&c=0,1,2,3,4,6,7,8,65,67,68'

MA_S=4
MA_M=10
MA_SL=30
MA_L=40

# 開始時刻
start_time=`date +%s`

# ディレクトリ構造の準備
mkdir -p $STOCK_DIR
mkdir -p $OUT_DIR
mkdir -p $(dirname $SCREEN_DATA2)
mkdir -p $(dirname $RS_CSV1)
touch $SCREEN_DATA2 # Ensure index file exists

# 古い出力ファイルのクリア
rm -rf $OUT_DIR/*

echo "1. Creating Ticker List..."
# スクリーニング＋銘柄リスト作成
python $SCRIPT_DIR/getList_US.py $SCREEN_DATA1 "$URL"

echo "2. Starting Screening..."
# 株価データダウンロード・判定
python $SCRIPT_DIR/chkData.py $SCREEN_DATA1 $STOCK_DIR $OUT_FILE1 $OUT_DIR $MA_S $MA_M $MA_SL $MA_L $INTVAL $RS_CSV1 $RS_CSV2 "America/New_York"
if [ -f "$SCREEN_DATA2" ]; then
    python $SCRIPT_DIR/chkData.py $SCREEN_DATA2 $STOCK_DIR $OUT_FILE1 $OUT_DIR $MA_S $MA_M $MA_SL $MA_L $INTVAL $RS_CSV1 $RS_CSV2 "America/New_York"
fi

echo "3. Checking Trend Template..."
# トレンド・テンプレート判定
python $SCRIPT_DIR/isTrend.py $STOCK_DIR $OUT_FILE2 $OUT_DIR/Trend- $MA_S $MA_M $MA_SL $MA_L $RS_CSV1 $RS_CSV2 $SCREEN_DATA1

# 終了時刻
end_time=`date +%s`

# 処理時間
run_time=$((end_time - start_time))

echo '-- END -- @' $run_time 'sec.'
