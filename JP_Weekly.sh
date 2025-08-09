#!/bin/bash

set -u

STOCK_DIR=/content/_files/JP/
SCREEN_DATA0=/content/_files/JP/data_j.xls
SCREEN_DATA1=/content/_files/JP/input.txt
SCREEN_DATA2=./_files/indexes/indexes_JP.txt
OUT_FILE1=./output_JP/sign.csv
OUT_FILE2=./output_JP/trend.csv
OUT_DIR=./output_JP/
MA_S=4
MA_M=10
MA_SL=30
MA_L=40
RS_CSV1=./_files/RS/rs_industries_jp.csv
RS_CSV2=./_files/RS/rs_stocks_jp.csv
IND_TXT=./_files/RS/industries_jp.txt
INTVAL=1wk

# 開始時刻
start_time=`date +%s`

# ディレクトリの移動
cd '/content/drive/My Drive/Screening/'

# 古い出力ファイルのクリア
rm -f $STOCK_DIR/*.*
rm -rf $OUT_DIR
mkdir $OUT_DIR

# スクリーニング＋銘柄リスト作成
python ./_scripts/getList_JP.py $SCREEN_DATA0 $SCREEN_DATA1 $STOCK_DIR $IND_TXT

# 株価データダウンロード・判定
python ./_scripts/chkData.py $SCREEN_DATA1 $STOCK_DIR $OUT_FILE1 $OUT_DIR $MA_S $MA_M $MA_SL $MA_L $INTVAL $RS_CSV1 $RS_CSV2
python ./_scripts/chkData.py $SCREEN_DATA2 $STOCK_DIR $OUT_FILE1 $OUT_DIR $MA_S $MA_M $MA_SL $MA_L $INTVAL $RS_CSV1 $RS_CSV2

# トレンド・テンプレート判定
python ./_scripts/isTrend.py $STOCK_DIR $OUT_FILE2 $OUT_DIR/Trend- $MA_S $MA_M $MA_SL $MA_L $RS_CSV1 $RS_CSV2 $SCREEN_DATA1

# 終了時刻
end_time=`date +%s`

# 処理時間
run_time=$((end_time - start_time))

echo '-- END -- @' $run_time 'sec.'
