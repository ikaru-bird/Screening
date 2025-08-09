# coding: UTF-8

# Googleドライブのライブラリを指定(for Google Colab)
import sys
sys.path.append('/content/drive/MyDrive/Colab Notebooks/my-modules')

import os, fnmatch
from classCheckData import CheckData

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

# データ処理クラスの作成
ckdt = CheckData(out_file, chart_dir, ma_short, ma_mid, ma_s_long, ma_long, rs_csv1, rs_csv2, txt_path)

# 探索ディレクトリ内をループ処理
for path, dirs, files in os.walk(in_dir):
    for filename in files:
        if not fnmatch.fnmatch(filename, "*.csv"): continue # CSVファイルの拡張子かをパターン・マッチング
        doc = os.path.abspath(os.path.join(path, filename)) # CSVファイルへの絶対パスを作成

        # csvをDataframeに格納
        ckdt.csvSetDF(doc)

        # 処理呼び出し
        print('TICKER:{0}'.format(ckdt.strTicker))

        # 判定処理呼び出し
        ckdt.isTrendTempleteAll()
        print('--')

# データ処理クラスの破棄
del ckdt

