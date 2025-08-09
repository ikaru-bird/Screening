#!/bin/bash

set -u

SCREEN_DATA1=./_files/RS/input_us.txt
SCREEN_DATA2=./_files/RS/input_nq100.txt
SCREEN_DATA3=./_files/indexes/Sector_ETF_US.txt
URL1="https://finviz.com/screener.ashx?v=152&f=cap_smallover,ind_stocksonly,sh_price_o7&o=-marketcap&c=0,1,2,3,4,6,7,8,65,67,68"
URL2="https://finviz.com/screener.ashx?v=152&f=idx_ndx&c=0,1,2,3,4,6,7,8,65,67,68"
IND_TXT=./_files/RS/industries_jp.txt
RS_RESULT1=./_files/RS/rs_stocks_us.csv
RS_RESULT2=./_files/RS/rs_stocks_jp.csv
RS_RESULT3=./_files/RS/rs_stocks_nq100.csv
RS_RESULT4=./_files/RS/rs_sector_etf_us.csv
RS_SECTOR1=./_files/RS/rs_industries_us.csv
RS_SECTOR2=./_files/RS/rs_industries_jp.csv
RS_SECTOR3=./_files/RS/rs_industries_nq100.csv
RS_SECTOR4=./_files/RS/rs_sector_us.csv
RS_IMG1=./_files/RS/rs_industries_us.png
RS_IMG2=./_files/RS/rs_industries_jp.png
RS_MOMENTUM1=./_files/RS/rs_momentum_us.png
RS_MOMENTUM2=./_files/RS/rs_momentum_jp.png
RS_MOMENTUM4=./_files/RS/rs_sector_us.png

# 開始時刻
start_time=`date +%s`

# ディレクトリの移動
cd '/content/drive/My Drive/Screening/'

# 銘柄リストの作成
python ./_scripts/getList_US.py $SCREEN_DATA1 $URL1
python ./_scripts/getList_US.py $SCREEN_DATA2 $URL2

# Relative-Strengthの計算処理の実行
python ./_scripts/relative-strength-us.py $SCREEN_DATA1 $RS_RESULT1 $RS_SECTOR1
python ./_scripts/relative-strength-jp.py $RS_RESULT2 $RS_SECTOR2 $IND_TXT
python ./_scripts/relative-strength-us.py $SCREEN_DATA2 $RS_RESULT3 $RS_SECTOR3
python ./_scripts/relative-strength-us.py $SCREEN_DATA3 $RS_RESULT4 $RS_SECTOR4

# セクター別RS一覧作成
python ./_scripts/SectorRS_US.py $RS_SECTOR1 $RS_IMG1
python ./_scripts/SectorRS_JP.py $RS_SECTOR2 $RS_IMG2

# セクターのRS Momentumの計算処理の実行
python ./_scripts/RS_Momentum.py $RS_SECTOR1 $RS_MOMENTUM1 10
python ./_scripts/RS_Momentum.py $RS_SECTOR2 $RS_MOMENTUM2 10
python ./_scripts/RS_Momentum.py $RS_SECTOR4 $RS_MOMENTUM4 11

# 終了時刻
end_time=`date +%s`

# 処理時間
run_time=$((end_time - start_time))

echo '-- END -- @' $run_time 'sec.'
