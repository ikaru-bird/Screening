# Googleドライブのライブラリを指定(for Google Colab)
import sys
sys.path.append('/content/drive/MyDrive/Colab Notebooks/my-modules')

import os
import math
import numpy as np
import pandas as pd
import random
import yfinance as yf
from classCheckData import CheckData
from classEarningsInfo import EarningsInfo
from datetime import datetime, timedelta
import time

# パラメータの受取り
args        = sys.argv
in_path     = args[1]
out_dir     = args[2]
out_file    = args[3]
chart_dir   = args[4]
ma_short    = int(args[5])
ma_mid      = int(args[6])
ma_s_long   = int(args[7])
ma_long     = int(args[8])
dt_interval = args[9]
rs_csv1     = args[10]
rs_csv2     = args[11]

symbol = np.full((5000),0,dtype=object)

# データ処理クラスの作成
ckdt = CheckData(out_file, chart_dir, ma_short, ma_mid, ma_s_long, ma_long, rs_csv1, rs_csv2, in_path)

# inputファイルから銘柄群のシンボルを取得
i = 0
if(os.path.exists(in_path)):
    with open(in_path, 'r', encoding='utf-8') as f:
        for line in f.readlines():
            toks = line.strip().split('~')
            symbol[i] = toks[0]
            i += 1

# 銘柄数を記録(カウンタ調整のため-1する)
n = i - 1

# Windowsで使用不可なファイル名を指定
NG_list = ["COM","AUX","PRN","NUL"]

# 株価データの取得期間
end   = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
start = (datetime.now() - timedelta(days=2*365)).strftime("%Y-%m-%d")

# 銘柄数の分だけループ
for i in range(0, n + 1):
    ticker_str = str(symbol[i])
    if not ticker_str:
        continue

    print('--- {0}/{1}: Checking {2} ---'.format(str(i + 1), str(n + 1), ticker_str))

    # ==================================================
    # STAGE 1: FUNDAMENTAL SCREENING
    # ==================================================
    try:
        # yfinanceから情報を取得
        ticker_obj = yf.Ticker(ticker_str)
        info = ticker_obj.info
        roe = info.get('returnOnEquity')

        # yfinanceオブジェクトを渡してEarningsInfoを作成
        ern_info = EarningsInfo(ticker_obj)

        # ファンダメンタルズ条件をチェック
        passed, results = ern_info.get_fundamental_screening_results(roe)

        # ログとしてチェック結果を表示
        for check_name, (res, reason) in results.items():
            status = "O" if res else "X"
            print(f"  - {status} : {check_name} : {reason}")

        if not passed:
            print(f"-> {ticker_str} did not pass fundamental screening. Skipping.\n")
            continue

    except Exception as e:
        print(f"##ERROR## Could not perform fundamental screen for {ticker_str}: {e}\n")
        continue

    print(f"-> {ticker_str} PASSED fundamental screening. Proceeding to technical analysis.")

    # ==================================================
    # STAGE 2: TECHNICAL ANALYSIS (Price Data)
    # ==================================================
    symbol_data = None

    # 使用できないファイル名の場合、ファイル名を変更
    if ticker_str in NG_list:
        fileName = str(out_dir) + ticker_str + '-X.csv'
    else:
        fileName = str(out_dir) + ticker_str + '.csv'

    # 株価データのダウンロード（最大3回リトライ）
    for j in range(3):
        try:
            if dt_interval == "1wk":
                symbol_data = ticker_obj.history(start=start, end=end, interval="1wk", auto_adjust=True)
            else:
                symbol_data = ticker_obj.history(start=start, end=end, interval="1d", auto_adjust=True)

            if symbol_data.empty:
                raise ValueError("No price data downloaded")

            if isinstance(symbol_data.columns, pd.MultiIndex):
                symbol_data.columns = symbol_data.columns.droplevel(1)

            break # success
        except Exception as e:
            print(f"##ERROR## Downloading price data for {ticker_str}: {e}. Retry {j+1}/3")
            time.sleep(5)

    if symbol_data is None or symbol_data.empty:
        print(f"-> Could not download price data for {ticker_str}. Skipping.\n")
        continue

    # テクニカル分析の実行
    try:
        symbol_data.to_csv(fileName, header=True, index=True)

        # 取得済みの決算情報をセット
        ckdt.set_earnings_info(ern_info)

        # DFをセット
        ckdt.csvSetDF(fileName)

        # 売買サイン判定の呼び出し
        ckdt.isTrendTemplete()
        ckdt.isON_Minervini()
        ckdt.isGranville()
        ckdt.isGoldernCross()
        print(f"-> Finished technical analysis for {ticker_str}.\n")

    except Exception as e:
        print(f"##ERROR## during technical analysis for {ticker_str}: {e}\n")
        continue

    # ループの最後に短いスリープを入れる
    time.sleep(random.randrange(200,1000,31)/1000)

# データ処理クラスの破棄
del ckdt
