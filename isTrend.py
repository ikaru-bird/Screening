# coding: UTF-8

import sys
import os, fnmatch
import yfinance as yf
from classCheckData import CheckData
from classEarningsInfo import EarningsInfo

# パラメータの受取り
args      = sys.argv
in_dir    = args[1]
out_file  = args[2]
chart_dir = args[3]
ma_short  = int(args[4])
ma_mid    = int(args[5])
ma_s_long = int(args[6])
ma_long   = int(args[7])
rs_csv1   = args[8]
rs_csv2   = args[9]
txt_path  = args[10]
dt_interval = args[11] if len(args) > 11 else '1d'

# データ処理クラスの作成
ckdt = CheckData(out_file, chart_dir, ma_short, ma_mid, ma_s_long, ma_long, rs_csv1, rs_csv2, txt_path, dt_interval=dt_interval)

# 探索ディレクトリ内をループ処理
for path, dirs, files in os.walk(in_dir):
    for filename in files:
        if not fnmatch.fnmatch(filename, "*.csv"): continue # CSVファイルの拡張子かをパターン・マッチング
        doc = os.path.abspath(os.path.join(path, filename)) # CSVファイルへの絶対パスを作成

        # csvをDataframeに格納
        ckdt.csvSetDF(doc)

        # 決算情報をセット
        try:
            ticker_obj = yf.Ticker(ckdt.strTicker)
            try:
                ticker_info = ticker_obj.info
            except Exception:
                ticker_info = {} # infoが取得できない場合は空の辞書を渡す
            ern_info = EarningsInfo(ticker_obj, ticker_info)
            ckdt.set_earnings_info(ern_info)
        except Exception as e:
            print(f"Could not fetch earnings info for {ckdt.strTicker}: {e}")
            # エラーが発生しても処理は続行

        # 処理呼び出し
        print('TICKER:{0}'.format(ckdt.strTicker))

        # 判定処理呼び出し
        ckdt.isTrendTempleteAll()
        ckdt.isBuySign()
        ckdt.isGranville()
        ckdt.isGoldernCross()
        ckdt.isON_Minervini()
        print('--')

# データ処理クラスの破棄
del ckdt
