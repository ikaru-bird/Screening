#!/bin/bash

set -u

STOCK_DIR1=/content/_files/US/
STOCK_DIR2=/content/_files/US-INDEX/
SCREEN_DATA1=/content/_files/US/input.txt
SCREEN_DATA2=./_files/indexes/indexes_US.txt
URL='https://finviz.com/screener.ashx?v=152&f=fa_epsqoq_o10,fa_epsyoy_o10,ind_stocksonly,sh_price_o10&ft=2&o=-marketcap&c=0,1,2,3,4,6,7,8,65,67,68'
OUT_FILE1=./output_US/sign.csv
OUT_FILE2=./output_US/trend.csv
OUT_DIR=./output_US/
MA_S=10
MA_M=50
MA_SL=150
MA_L=200
RS_CSV1=./_files/RS/rs_industries_us.csv
RS_CSV2=./_files/RS/rs_stocks_us.csv
INTVAL=1d

# 開始時刻
start_time=`date +%s`

# ディレクトリの移動
cd '/content/drive/My Drive/Screening/'

# 古い出力ファイルのクリア
rm -f $STOCK_DIR1/*.*
rm -f $STOCK_DIR2/*.*
rm -rf $OUT_DIR
mkdir $OUT_DIR

# スクリーニング＋銘柄リスト作成
python ./_scripts/getList_US.py $SCREEN_DATA1 $URL

# 株価データダウンロード・判定
python ./_scripts/chkData.py $SCREEN_DATA1 $STOCK_DIR1 $OUT_FILE1 $OUT_DIR $MA_S $MA_M $MA_SL $MA_L $INTVAL $RS_CSV1 $RS_CSV2
python ./_scripts/chkData.py $SCREEN_DATA2 $STOCK_DIR2 $OUT_FILE1 $OUT_DIR $MA_S $MA_M $MA_SL $MA_L $INTVAL $RS_CSV1 $RS_CSV2

# トレンド・テンプレート判定(INDEXのみ)
python ./_scripts/isTrend.py $STOCK_DIR2 $OUT_FILE2 $OUT_DIR/Trend- $MA_S $MA_M $MA_SL $MA_L $RS_CSV1 $RS_CSV2 $SCREEN_DATA2

# 終了時刻
end_time=`date +%s`

# 処理時間
run_time=$((end_time - start_time))

echo '-- END -- @' $run_time 'sec.'
