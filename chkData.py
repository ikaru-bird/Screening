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
            toks = line.split('~')
            symbol[i] = toks[0]
            i += 1

# 銘柄数を記録(カウンタ調整のため-1する)
n = i - 1

# Windowsで使用不可なファイル名を指定
NG_list = ["COM","AUX","PRN","NUL"]

# 株価データの取得期間
# end = datetime.now().strftime("%Y-%m-%d")
end   = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
start = (datetime.now() - timedelta(days=2*365)).strftime("%Y-%m-%d")

# 銘柄数の分だけループ
for i in range(0, n+1):
#   print(str(symbol[i]))
    print('TICKER:{0} ({1}/{2})'.format(str(symbol[i]), str(i+1), str(n+1)))
    symbol_data = None

    # 使用できないファイル名の場合、ファイル名を変更
    if symbol[i] in NG_list:
        # 保存ファイル名の指定
        fileName = str(out_dir) + str(symbol[i])+'-X.csv'
    else:
        # 保存ファイル名の指定
        fileName = str(out_dir) + str(symbol[i])+'.csv'

    # 最大3回実行
    for j in range(3):
        try:
            # 株価データ読み込み
            if dt_interval == "1wk":
                symbol_data = yf.download(symbol[i], start=start, end=end, interval="1wk", auto_adjust=True)
            else:
                symbol_data = yf.download(symbol[i], start=start, end=end, interval="1d", auto_adjust=True)
            # 不要なインデックスレベルを削除
            if isinstance(symbol_data.columns, pd.MultiIndex):
                symbol_data.columns = symbol_data.columns.droplevel(1)
        except:
            print("\r##ERROR##: Retry=%s" % (str(j)), end="\n", flush=True)
            time.sleep(5)  # 5秒スリープしてリトライ
        else:
            # 不要な行を除去
            symbol_data.to_csv(fileName, header=True, index=True)
            
            # csvをDataframeに格納
            ckdt.csvSetDF(fileName)
            
            # 売買サイン判定の呼び出し
            ckdt.isTrendTemplete()  # トレンドテンプレート該当銘柄からPivotを探す
            ckdt.isON_Minervini()   # オニール、ミネルヴィ・ニパターンを探す
            ckdt.isGranville()      # 買いポイントを探す
            ckdt.isGoldernCross()   # GoldernCrossを探す
#           ckdt.isShortSign()      # 空売りパターンを探す
            print('--')
            
            break  # ループを抜ける

    # 過度なアクセスを防ぐために時間（ランダム0.2～1秒）空ける
    time.sleep(random.randrange(200,1000,31)/1000)

# データ処理クラスの破棄
del ckdt
