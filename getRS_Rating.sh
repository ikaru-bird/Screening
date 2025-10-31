#!/bin/bash

set -u

# Corrected paths for the sandbox environment
BASE_DIR=.
SCREEN_DATA1=$BASE_DIR/_files/RS/input_us.txt
SCREEN_DATA2=$BASE_DIR/_files/RS/input_nq100.txt
SCREEN_DATA3=$BASE_DIR/_files/indexes/Sector_ETF_US.txt
IND_TXT=$BASE_DIR/_files/RS/industries_jp.txt
RS_RESULT1=$BASE_DIR/_files/RS/rs_stocks_us.csv
RS_RESULT2=$BASE_DIR/_files/RS/rs_stocks_jp.csv
RS_RESULT3=$BASE_DIR/_files/RS/rs_stocks_nq100.csv
RS_RESULT4=$BASE_DIR/_files/RS/rs_sector_etf_us.csv
RS_SECTOR1=$BASE_DIR/_files/RS/rs_industries_us.csv
RS_SECTOR2=$BASE_DIR/_files/RS/rs_industries_jp.csv
RS_SECTOR3=$BASE_DIR/_files/RS/rs_industries_nq100.csv
RS_SECTOR4=$BASE_DIR/_files/RS/rs_sector_us.csv
RS_IMG1=$BASE_DIR/_files/RS/rs_industries_us.png
RS_IMG2=$BASE_DIR/_files/RS/rs_industries_jp.png
RS_MOMENTUM1=$BASE_DIR/_files/RS/rs_momentum_us.png
RS_MOMENTUM2=$BASE_DIR/_files/RS/rs_momentum_jp.png
RS_MOMENTUM4=$BASE_DIR/_files/RS/rs_sector_us.png
SCRIPT_DIR=$BASE_DIR/_scripts

# Original URLs with specific criteria for this script
URL1="https://finviz.com/screener.ashx?v=152&f=cap_smallover,ind_stocksonly,sh_price_o7&o=-marketcap&c=0,1,2,3,4,6,7,8,65,67,68"
URL2="https://finviz.com/screener.ashx?v=152&f=idx_ndx&c=0,1,2,3,4,6,7,8,65,67,68"


# 開始時刻
start_time=`date +%s`

# ディレクトリ構造の準備
mkdir -p $(dirname $SCREEN_DATA1)
mkdir -p $(dirname $SCREEN_DATA3)
touch $SCREEN_DATA3

echo "1. Creating Ticker Lists for RS Rating..."
# 銘柄リストの作成
python $SCRIPT_DIR/getList_US.py $SCREEN_DATA1 "$URL1"
python $SCRIPT_DIR/getList_US.py $SCREEN_DATA2 "$URL2"

echo "2. Calculating Relative Strength..."
# Relative-Strengthの計算処理の実行
# Note: relative-strength scripts are not in the repo, these lines will fail.
python $SCRIPT_DIR/relative-strength-us.py $SCREEN_DATA1 $RS_RESULT1 $RS_SECTOR1
python $SCRIPT_DIR/relative-strength-jp.py $RS_RESULT2 $RS_SECTOR2 $IND_TXT
python $SCRIPT_DIR/relative-strength-us.py $SCREEN_DATA2 $RS_RESULT3 $RS_SECTOR3
python $SCRIPT_DIR/relative-strength-us.py $SCREEN_DATA3 $RS_RESULT4 $RS_SECTOR4

echo "3. Creating RS Charts..."
# セクター別RS一覧作成
# python $SCRIPT_DIR/SectorRS_US.py $RS_SECTOR1 $RS_IMG1
# python $SCRIPT_DIR/SectorRS_JP.py $RS_SECTOR2 $RS_IMG2
python $SCRIPT_DIR/createRsHeatmap.py US $RS_SECTOR1 $RS_IMG1
python $SCRIPT_DIR/createRsHeatmap.py JP $RS_SECTOR2 $RS_IMG2

echo "4. Calculating RS Momentum..."
# セクターのRS Momentumの計算処理の実行
# python $SCRIPT_DIR/RS_Momentum.py $RS_SECTOR1 $RS_MOMENTUM1 10
# python $SCRIPT_DIR/RS_Momentum.py $RS_SECTOR2 $RS_MOMENTUM2 10
# python $SCRIPT_DIR/RS_Momentum.py $RS_SECTOR4 $RS_MOMENTUM4 11

# 終了時刻
end_time=`date +%s`

# 処理時間
run_time=$((end_time - start_time))

echo '-- END -- @' $run_time 'sec.'
