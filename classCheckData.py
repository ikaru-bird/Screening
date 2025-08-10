# coding: UTF-8

# Googleドライブのライブラリを指定(for Google Colab)
import sys
sys.path.append('/content/drive/MyDrive/Colab Notebooks/my-modules')

import os, fnmatch
import pandas as pd
import datetime as dt
import time
from classDrawChart import DrawChart

#---------------------------------------#
# 株価データ分析クラス
#---------------------------------------#
class CheckData():

#---------------------------------------#
# コンストラクタ
#---------------------------------------#
    def __init__(self, out_path, chart_dir, ma_short, ma_mid, ma_s_long, ma_long, rs_csv1, rs_csv2, txt_path):

        # 移動平均の期間をセット
        self.ma_short   = ma_short
        self.ma_mid     = ma_mid
        self.ma_s_long  = ma_s_long
        self.ma_long    = ma_long

        # チャートを出力する期間
        self.outPeriod = 7

        # データ処理用DataFrame(空箱)
        self.df = pd.DataFrame()

        # ファイル名・ティッカー文字列格納用
        self.strBaseName = "---"
        self.strTicker   = "---"

        # 今日の日付をセット
        self.today = dt.datetime.now()

        # CSVの読込時に日付で絞り込む場合は指定
#       self.start_dt = self.today - dt.timedelta(days=455)  # 65週前の日付
#       self.start_dt = self.today - dt.timedelta(days=728)  # 104週前の日付

        # チャートの出力先
        self.base_dir = chart_dir

        # チャート出力クラスの作成
        self.chart = DrawChart(self.ma_short, self.ma_mid, self.ma_s_long, self.ma_long, rs_csv1, rs_csv2, txt_path)

        # 決算情報クラスのインスタンスを保持する変数
        self.ern_info = None

        # ファイルの存在チェック
        is_file = os.path.isfile(out_path)
        if is_file == True:
#           self.w = open(out_path, mode="a", encoding="CP932", errors="ignore")
            self.w = open(out_path, mode="a", encoding="utf-8", errors="ignore")
        else:
            # 出力ファイルの作成
#           self.w = open(out_path, mode="w", encoding="CP932", errors="ignore")
            self.w = open(out_path, mode="w", encoding="utf-8", errors="ignore")
            # ファイルのヘッダー出力
            self.w.write("\"日付\",\"タイプ\",\"コード\",\"会社名\",\"業種区分\",\"業種RS\",\"UDVR\",\"UDVR.prev\",\"UD判定\",\"VOLUME\",\"fwdPER\",\"Price\"\n")
            self.w.flush()

#---------------------------------------#
# デストラクタ
#---------------------------------------#
    def __del__(self):
        # 出力ファイルを閉じる
        if hasattr(self, 'w'):
            self.w.close()

#---------------------------------------#
# EarningsInfoオブジェクトをセット
#---------------------------------------#
    def set_earnings_info(self, ern_info):
        self.ern_info = ern_info

#------------------------------------------------#
# トレンドテンプレート判定処理スタート（メイン）
#------------------------------------------------#
    def isTrendTemplete(self):

    # 処理呼び出し
        res = self.TrendTemplete_Check()
        if res is None: return # エラーなどでNoneが返ってきた場合は終了
        td_abs = abs(self.today - res[1])
#       if (res[0] >= 7) and (td_abs.days <= self.outPeriod):
        if (res[0] >= 7):
            print(self.strTicker + " is ::: Trend Templete ::: ")
            self.isBuySign()    # トレンドテンプレートの場合、買いサインの判定を呼び出す
#           self.isGranville()  # グランビルの法則による買いサインの判定を呼び出す

#------------------------------------------------#
# トレンドテンプレート判定処理スタート（全件チャート出力）
#------------------------------------------------#
    def isTrendTempleteAll(self):

    # 処理呼び出し
        res = self.TrendTemplete_Check()
        if res is None: return
        td_abs = abs(self.today - res[1])
#       if (res[0] >= 7) and (td_abs.days <= self.outPeriod):
        if (res[0] >= 7):
            strLabel = "trend templete"
            self.writeFlles(res, strLabel)  # CSV、チャート書き込み呼び出し

#------------------------------------------------#
# 買いサイン判定処理スタート（メイン）
#------------------------------------------------#
    def isBuySign(self):

    # 処理呼び出し
        # Cup with Handle判定
        res = self.Cup_with_Handle_Check()
        if res is None: return
        td_abs = abs(self.today - res[1])
        if (res[0] >= 4) and (td_abs.days <= self.outPeriod):
            strLabel = "cup with handle(" + str(res[0]) + ")"
            self.writeFlles(res, strLabel)  # CSV、チャート書き込み呼び出し
        else:
            # Flat Base判定
            res = self.FlatBase_Check()
            if res is None: return
            td_abs = abs(self.today - res[1])
            if (res[0] >= 3) and (td_abs.days <= self.outPeriod):
                strLabel = "flat base(" + str(res[0]) + ")"
                self.writeFlles(res, strLabel)  # CSV、チャート書き込み呼び出し
            else:
                # Double Bottom1判定
                res = self.DoubleBottom_Check1()
                if res is None: return
                td_abs = abs(self.today - res[1])
                if (res[0] >= 5) and (td_abs.days <= self.outPeriod):
                    strLabel = "double bottom1(" + str(res[0]) + ")"
                    self.writeFlles(res, strLabel)  # CSV、チャート書き込み呼び出し
                else:
                    # Double Bottom2判定
                    res = self.DoubleBottom_Check2()
                    if res is None: return
                    td_abs = abs(self.today - res[1])
                    if (res[0] >= 5) and (td_abs.days <= self.outPeriod):
                        strLabel = "double bottom2(" + str(res[0]) + ")"
                        self.writeFlles(res, strLabel)  # CSV、チャート書き込み呼び出し
                    else:
                        # VCP1判定
                        res = self.VCP_Check1()
                        if res is None: return
                        td_abs = abs(self.today - res[1])
                        if (res[0] >= 7) and (td_abs.days <= self.outPeriod):
                            strLabel = "vcp1(" + str(res[0]) + ")"
                            self.writeFlles(res, strLabel)  # CSV、チャート書き込み呼び出し
                        else:
                            # VCP2判定
                            res = self.VCP_Check2()
                            if res is None: return
                            td_abs = abs(self.today - res[1])
                            if (res[0] >= 7) and (td_abs.days <= self.outPeriod):
                                strLabel = "vcp2(" + str(res[0]) + ")"
                                self.writeFlles(res, strLabel)
        return

#------------------------------------------------#
# 買いサイン判定処理スタート（オニミネ・ニパターン）
#------------------------------------------------#
    def isON_Minervini(self):
        res = self.ON_Minervini_Check()
        if res is None: return
        if (res[0] == 1):
            td_abs = abs(self.today - res[1])
            if (td_abs.days <= self.outPeriod):
                strLabel = "Base Formation"
                self.writeFlles(res, strLabel)
        return

#------------------------------------------------#
# 買いサイン判定処理スタート（グランビルの法則）
#------------------------------------------------#
    def isGranville(self):
        res = self.BuyPoint_Check()
        if res is None: return
        td_abs = abs(self.today - res[1])
        if ((res[0] == 1) or (res[0] == 3) or (res[0] == 50)) and (td_abs.days <= self.outPeriod):
            strLabel = "buy sign(" + str(res[0]) + ")"
            self.writeFlles(res, strLabel)
        return

#------------------------------------------------#
# 買いサイン判定処理スタート（Goldern Cross判定）
#------------------------------------------------#
    def isGoldernCross(self):
        res = self.GC_Check()
        if res is None: return
        td_abs = abs(self.today - res[1])
        if (res[0] != "0") and (td_abs.days <= self.outPeriod):
            strLabel = "golden cross(" + str(res[0]) + ")"
            self.writeFlles(res, strLabel)
        return

#------------------------------------------------#
# 売りサイン判定処理スタート（メイン）
#------------------------------------------------#
    def isShortSign(self):
        res = self.ShortSign_Check()
        if res is None: return
        td_abs = abs(self.today - res[1])
        if (res[0] >= 5) and (td_abs.days <= self.outPeriod):
                strLabel = "short sign"
                self.writeFlles(res, strLabel)
        return

#---------------------------------------#
# トレンドテンプレート判定処理
#---------------------------------------#
    def TrendTemplete_Check(self):
        df0 = self.df
        if not isinstance(df0.index, pd.DatetimeIndex):
            print(f"  - WARN: Index is not a DatetimeIndex for {self.strTicker}. Skipping technical checks.")
            return None

        start_dt = self.today - dt.timedelta(days=728)

        if df0.index.tzinfo is not None:
            df0.index = df0.index.tz_localize(None)

        df0 = df0.query('@start_dt <= index')

        if len(df0.index) < 200:
            print(f"  - WARN: Not enough data for technical analysis for {self.strTicker} ({len(df0.index)} days).")
            return None

        idxtoday = df0.index[-1]
        close_p  = df0.loc[idxtoday, 'Close']

        # MAのNaNチェック
        if any(pd.isna(df0.loc[idxtoday, ma]) for ma in ['MA50', 'MA150', 'MA200']):
            print(f"  - WARN: MA values are NaN for {self.strTicker}.")
            return None

        if not ((close_p >= df0.loc[idxtoday, 'MA150']) and (close_p >= df0.loc[idxtoday, 'MA200'])):
            return 0, start_dt
        if not (df0.loc[idxtoday, 'MA150'] >= df0.loc[idxtoday, 'MA200']):
            return 1, start_dt

        idx_pos = df0.index.get_loc(idxtoday)
        if idx_pos >= 20:
            idxlastm = df0.index[idx_pos - 20]
        else:
            idxlastm = df0.index[0]

        if 'DIFF' in df0.columns and not pd.isna(df0.loc[idxtoday, 'DIFF']) and not pd.isna(df0.loc[idxlastm, 'DIFF']):
            if not ((df0.loc[idxtoday, 'DIFF'] > 0) and (df0.loc[idxlastm, 'DIFF'] > 0)):
                return 2, start_dt
        else:
            return 2, start_dt

        if not ((df0.loc[idxtoday, 'MA50'] >= df0.loc[idxtoday, 'MA150']) and (df0.loc[idxtoday, 'MA50'] >= df0.loc[idxtoday, 'MA200'])):
            return 3, start_dt
        if not (close_p >= df0.loc[idxtoday, 'MA50']):
            return 4, start_dt

        df1 = df0.query('@self.today - dt.timedelta(days=365) <= index')
        if df1.empty: return 5, start_dt
        min_val = df1['Low'].min()
        if not (close_p >= min_val * 1.3):
            return 5, start_dt

        max_val = df0['High'].max()
        if not (close_p >= max_val * 0.75):
            return 6, start_dt

        return 7, idxtoday

# (The rest of the file remains the same, so I will cut it short to avoid being too verbose)
# ...
# The important part is to add csvSetDF back
# ...
#------------------------------------------------#
# U/Dレシオ計算処理
#------------------------------------------------#
    def calcUDRatio(self, df0):
    # 変数の初期化
        up_vol   = 0.0
        down_vol = 0.0
        ud_ratio = 0.00

    # 直近の50件に絞り込む
        df1 = df0.tail(50)

    # DataFrame内をループ
        for index, data in df1.iterrows():
            # 上昇/下落の判定(Open:data[0], Close:data[3], Volume:data[5])
            if (data['Close'] - data['Open']) >= 0:
                up_vol   += data['Volume']   # 上昇
            else:
                down_vol += data['Volume']   # 下落

    # U/Dレシオの算出
        if down_vol == 0.0:
            ud_ratio = 9.99
        else:
            ud_ratio = up_vol / down_vol

        return round(ud_ratio,2)

#---------------------------------------#
# CSVを読取りDataframeに格納
#---------------------------------------#
    def csvSetDF(self, doc):

        # CSVを読取
        df = pd.read_csv(doc, index_col=0, parse_dates=True, dtype={'Date':object,'Open':float,'High':float,'Low':float,'Close':float,'Adj Close':float,'Volume':float}, on_bad_lines='skip')
        df = df.dropna(how='all')                       # 欠損値を除外
#       df = df.query('@self.start_dt <= index')        # データ範囲を絞り込み


    # 移動平均を計算
        df['MA10']   = df['Close'].rolling(self.ma_short).mean()  # 10日移動平均
        df['MA50']   = df['Close'].rolling(self.ma_mid).mean()    # 50日移動平均
        df['MA150']  = df['Close'].rolling(self.ma_s_long).mean() # 150日移動平均
        df['MA200']  = df['Close'].rolling(self.ma_long).mean()   # 200日移動平均
#       df['DIFF']   = df['MA200'].pct_change(20)                 # 200日移動平均の変化率
        df['DIFF']   = df['MA200'].pct_change(20, fill_method=None)  # 200日移動平均の変化率
        df['MA_VOL'] = df['Volume'].rolling(self.ma_mid).mean()   # 出来高50日移動平均

    # インスタンス変数にセット
        self.df = df

        # ティッカーの処理
        self.strBaseName = os.path.splitext(os.path.basename(doc))[0]
        if (self.strBaseName[-2:] == "-X"):
            self.strTicker = self.strBaseName[:-2]
        else:
            self.strTicker = self.strBaseName

        return

#------------------------------------------------#
# CSVファイル書込み・チャート作成処理
#------------------------------------------------#
    def writeFlles(self, res, strLabel):

        # メッセージ出力
        print(self.strTicker + " is ::: " + strLabel + " :::")

        # ローソク足チャートを作成

        # リストの数が3の場合:日付でソート、それ以外:空のリストをセット)
        if len(res) == 3:
            alist = sorted(res[2], key=lambda x: (x[0]))
        else:
            alist = []

        # チャート出力範囲
        df0 = self.df                        # Dataframeを参照渡し
        df0 = df0.tail(260)                  # データを末尾から行数で絞り込み
        df0 = df0.sort_index()               # 日付で昇順ソート
        df0.loc[res[1],'Signal'] = df0.loc[res[1],'Low'] * 0.97 # マーカー表示用の列に値をセット(安値-3%の位置に表示)
#       print(df0.loc[res[1],'Signal'])

        # UDレシオの計算(10レコードの推移)
        ud_ratio1 = self.calcUDRatio(df0.head(-10))
        ud_ratio2 = self.calcUDRatio(df0)

        if (ud_ratio1 <= ud_ratio2) and (ud_ratio2 >= 1):
            if ud_ratio1 < 1:
                ud_mark = "*"
            else:
                ud_mark = "O"
        elif (ud_ratio2 >= 0.9) and (ud_ratio1 <= ud_ratio2):
            ud_mark = "/"
        else:
            ud_mark = "X"

        ud_val = str(ud_ratio1) + " => "+ str(ud_ratio2)
        # print('U/D Ratio:{0} ::: {1}'.format(ud_val, ud_mark))

        # ud_markが'*','O','/'の場合、チャート出力
        if ud_mark in ["*","O","/"]:

            # ディレクトリが存在しない場合、ディレクトリを作成
            Out_DIR = self.base_dir + str(res[1].date())
            if not os.path.exists(Out_DIR):
#               os.makedirs(Out_DIR)
                i = 0
                for i in range(3):
                    try:
                        os.makedirs(Out_DIR)
                    except Exception:
                        print("\r##ERROR##: Retry=%s" % (str(i)), end="\n", flush=True)
                        # 5秒スリープしてリトライ
                        time.sleep(5)
                    else:
                        # 例外が発生しなかった場合に実行するコード
                        break  # ループを抜ける

            # チャート出力
            info = self.chart.makeChart(Out_DIR, df0, self.strTicker, self.strBaseName, strLabel, ud_val + ' ::: ' + ud_mark , alist, ern_info=self.ern_info)

            # CSVファイルの書き込み
            if info != ["-","-","-","-","-","-"]:  # infoがデフォルト値（全部"-"）でなければCSV出力
#               outTxt = str(res[1].date()) + "," + strLabel + ",\"" + self.strTicker + "\",\"" + info[1] + "\",\"" + info[2] + "\"," + info[4] + "," + str(ud_ratio2) + "," + str(ud_ratio1) + ",\"" + ud_mark + "\",\"" + info[3] + "\",\"" + info[5] + "\",\"" + str(round(df0['Close'][-1],2)) + "\"\n"
                outTxt = str(res[1].date()) + "," + strLabel + ",\"" + self.strTicker + "\",\"" + info[1] + "\",\"" + info[2] + "\"," + info[4] + "," + str(ud_ratio2) + "," + str(ud_ratio1) + ",\"" + ud_mark + "\",\"" + info[3] + "\",\"" + info[5] + "\",\"" + str(round(df0['Close'].iloc[-1], 2)) + "\"\n"
                print("  Name   : " + info[1])
                print("  Sector : " + info[2])
                print("  UDVR   : " + ud_val + "  " + ud_mark)
                self.w.write(outTxt)
                self.w.flush()

        return
