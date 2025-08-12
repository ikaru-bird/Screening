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
            self.w.write("\"日付\",\"タイプ\",\"コード\",\"会社名\",\"業種区分\",\"業種RS\",\"UDVR\",\"UDVR.prev\",\"UD判定\",\"VOLUME\",\"Price\"\n")
            self.w.flush()

#---------------------------------------#
# デストラクタ
#---------------------------------------#
    def __del__(self):
        # 出力ファイルを閉じる
        self.w.close()

#---------------------------------------#
# 決算情報をセット
#---------------------------------------#
    def set_earnings_info(self, ern_info):
        self.ern_info = ern_info

#------------------------------------------------#
# トレンドテンプレート判定処理スタート（メイン）
#------------------------------------------------#
    def isTrendTemplete(self):

    # 処理呼び出し
        res = self.TrendTemplete_Check()
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
        td_abs = abs(self.today - res[1])
        if (res[0] >= 4) and (td_abs.days <= self.outPeriod):
            strLabel = "cup with handle(" + str(res[0]) + ")"
            self.writeFlles(res, strLabel)  # CSV、チャート書き込み呼び出し
        else:
            # Flat Base判定
            res = self.FlatBase_Check()
            td_abs = abs(self.today - res[1])
            if (res[0] >= 3) and (td_abs.days <= self.outPeriod):
                strLabel = "flat base(" + str(res[0]) + ")"
                self.writeFlles(res, strLabel)  # CSV、チャート書き込み呼び出し
            else:
                # Double Bottom1判定
                res = self.DoubleBottom_Check1()
                td_abs = abs(self.today - res[1])
                if (res[0] >= 5) and (td_abs.days <= self.outPeriod):
                    strLabel = "double bottom1(" + str(res[0]) + ")"
                    self.writeFlles(res, strLabel)  # CSV、チャート書き込み呼び出し
                else:
                    # Double Bottom2判定
                    res = self.DoubleBottom_Check2()
                    td_abs = abs(self.today - res[1])
                    if (res[0] >= 5) and (td_abs.days <= self.outPeriod):
                        strLabel = "double bottom2(" + str(res[0]) + ")"
                        self.writeFlles(res, strLabel)  # CSV、チャート書き込み呼び出し
                    else:
                        # VCP1判定
                        res = self.VCP_Check1()
                        td_abs = abs(self.today - res[1])
                        if (res[0] >= 7) and (td_abs.days <= self.outPeriod):
                            strLabel = "vcp1(" + str(res[0]) + ")"
                            self.writeFlles(res, strLabel)  # CSV、チャート書き込み呼び出し
                        else:
                            # VCP2判定
                            res = self.VCP_Check2()
                            td_abs = abs(self.today - res[1])
                            if (res[0] >= 7) and (td_abs.days <= self.outPeriod):
                                strLabel = "vcp2(" + str(res[0]) + ")"
                                self.writeFlles(res, strLabel)  # CSV、チャート書き込み呼び出し
#                            else:
#                                # ON_Minervini_Check
#                                res = self.ON_Minervini_Check()
#                                if (res[0] == 1):
#                                    td_abs = abs(self.today - res[1])
#                                    if (td_abs.days <= self.outPeriod):
#                                        strLabel = "Base Formation"
#                                        self.writeFlles(res, strLabel)  # CSV、チャート書き込み呼び出し
        return

#------------------------------------------------#
# 買いサイン判定処理スタート（オニミネ・ニパターン）
#------------------------------------------------#
    def isON_Minervini(self):

    # 処理呼び出し
        res = self.ON_Minervini_Check()
        if (res[0] == 1):
            td_abs = abs(self.today - res[1])
            if (td_abs.days <= self.outPeriod):
                strLabel = "Base Formation"
                self.writeFlles(res, strLabel)  # CSV、チャート書き込み呼び出し
        return

#------------------------------------------------#
# 買いサイン判定処理スタート（グランビルの法則）
#------------------------------------------------#
    def isGranville(self):

    # 処理呼び出し
        res = self.BuyPoint_Check()
        td_abs = abs(self.today - res[1])
        if ((res[0] == 1) or (res[0] == 3) or (res[0] == 50)) and (td_abs.days <= self.outPeriod):
            strLabel = "buy sign(" + str(res[0]) + ")"
            self.writeFlles(res, strLabel)  # CSV、チャート書き込み呼び出し
        return

#------------------------------------------------#
# 買いサイン判定処理スタート（Goldern Cross判定）
#------------------------------------------------#
    def isGoldernCross(self):

    # 処理呼び出し
        res = self.GC_Check()
        td_abs = abs(self.today - res[1])
        if (res[0] != "0") and (td_abs.days <= self.outPeriod):
            strLabel = "golden cross(" + str(res[0]) + ")"
            self.writeFlles(res, strLabel)  # CSV、チャート書き込み呼び出し
        return

#------------------------------------------------#
# 売りサイン判定処理スタート（メイン）
#------------------------------------------------#
    def isShortSign(self):

    # 処理呼び出し
        res = self.ShortSign_Check()

    # 出力ファイルへ書き込み（ステータスが5以上かつ指定日以内のの場合）
        td_abs = abs(self.today - res[1])
        if (res[0] >= 5) and (td_abs.days <= self.outPeriod):
                strLabel = "short sign"
                self.writeFlles(res, strLabel) # CSV、チャート書き込み呼び出し
        return

#---------------------------------------#
# トレンドテンプレート判定処理
#---------------------------------------#
    def TrendTemplete_Check(self):

    # Dataframeをセット
        df0 = self.df

        start_dt = self.today - dt.timedelta(days=728)  # 104週前の日付
        try:
            df0.index = df0.index.tz_localize(None)     # INDEXのタイムゾーンを取り除く
        except Exception as e:
            print(e)
        df0 = df0.query('@start_dt <= index')           # データ範囲を絞り込み

    # 直近の日付、終値
        if len(df0.index) > 0:
            idxtoday = df0.index[-1]
            close_p  = df0.loc[idxtoday, 'Close']
        else:
            return 0, start_dt

    # ① 終値が150日と200日移動平均線より上
        if (close_p >= df0.loc[idxtoday, 'MA150']) and (close_p >= df0.loc[idxtoday, 'MA200']):
            pass
        else:
            return 0, start_dt

    # ② 150日移動平均線が200日移動平均線より上
        if df0.loc[idxtoday, 'MA150'] >= df0.loc[idxtoday, 'MA200']:
            pass
        else:
            return 1, start_dt

    # ③ 200日移動平均線が少なくとも1ヵ月以上上昇トレンド
        idx_pos = df0.index.get_loc(idxtoday)
        if idx_pos >= 20:
            idxlastm = df0.index[idx_pos - 20]
        else:
            idxlastm = df0.index[0]  # データ不足時は最古の比較対象を使用
        if (df0.loc[idxtoday, 'DIFF'] > 0) and (df0.loc[idxlastm, 'DIFF'] > 0):
            pass
        else:
            return 2, start_dt

    # ④ 50日移動平均線が150日、200日移動平均線より上
        if (df0.loc[idxtoday, 'MA50'] >= df0.loc[idxtoday, 'MA150']) and (df0.loc[idxtoday, 'MA50'] >= df0.loc[idxtoday, 'MA200']):
            pass
        else:
            return 3, start_dt

    # ⑤ 現在の株価が50日移動平均線より上
        if close_p >= df0.loc[idxtoday, 'MA50']:
            pass
        else:
            return 4, start_dt

    # ⑥ 現在の株価が52週安値より少なくとも30％高い
        start_dt = self.today - dt.timedelta(days=365)  # 52週前の日付
        df1 = df0.query('@start_dt <= index')           # データ範囲を絞り込み

        rows   = df1['Low']
        min    = rows.min()
        idxmin = rows.idxmin()

        if close_p >= min * 1.3:
            pass
        else:
            return 5, start_dt

    # ⑦ 現在の株価は52週高値から25％以内
        rows   = df0['High']
        max    = rows.max()
        idxmax = rows.idxmax()

        if close_p >= max * 0.75:
            return 7, idxtoday
        else:
            return 6, start_dt

#---------------------------------------#
# 買いシグナル判定処理
#---------------------------------------#
    def BuyPoint_Check(self):

    # Dataframeをセット
        df0 = self.df
        start_dt = self.today - dt.timedelta(days=728)  # 104週前の日付
        df0 = df0.query('@start_dt <= index')           # データ範囲を絞り込み

    # 戻り値蓄積用リスト
        reslist = [[0,start_dt,0]]

    # 買い①：株価がMA200を超える（移動平均の傾きがプラス）
        try:
            df1 = df0.query('Close > MA200 and Close.shift(1) <= MA200.shift(1) and DIFF > 0.0005')
            if len(df1.index) > 0:
                buypoint_dt = df1.index[0]
                buypoint_p  = df1.loc[buypoint_dt, "Close"]
                reslist.append([1,buypoint_dt,df1.loc[buypoint_dt,"DIFF"]])
            else:
                pass
        except Exception as e:
            print(f"An error occurred: {e}")
            pass

    # 買い②：株価がMA200を下回る（移動平均の傾きがプラス）
        try:
            df1 = df0.query('Close < MA200 and Close.shift(1) >= MA200.shift(1) and DIFF > 0.0005')
            if len(df1.index) > 0:
                buypoint_dt = df1.index[0]
                buypoint_p  = df1.loc[buypoint_dt, "Close"]
                reslist.append([2,buypoint_dt,df1.loc[buypoint_dt,"DIFF"]])
            else:
                pass
        except Exception as e:
            print(f"An error occurred: {e}")
            pass

    # 買い③：株価がMA200上で反発（移動平均の傾きがプラス）
        try:
            df1 = df0.query('Close < MA10 and MA200 * 1.01 >= Close >= MA200 and DIFF > 0.0005')
            if len(df1.index) > 0:
                buypoint_dt = df1.index[0]
                buypoint_p  = df1.loc[buypoint_dt, "Close"]
                reslist.append([3,buypoint_dt,df1.loc[buypoint_dt,"DIFF"]])
            else:
                pass
        except Exception as e:
            print(f"An error occurred: {e}")
            pass

    # 買い④：株価がMA200を割って大きく下落（移動平均の傾きがプラス）
        try:
            df1 = df0.query('MA200 * 0.9 >= Close and DIFF > 0.0005')
            if len(df1.index) > 0:
                buypoint_dt = df1.index[0]
                buypoint_p  = df1.loc[buypoint_dt, "Close"]
                reslist.append([4,buypoint_dt,df1.loc[buypoint_dt,"DIFF"]])
            else:
                pass
        except Exception as e:
            print(f"An error occurred: {e}")
            pass

    # 買い⑤：株価がMA50プルバック（移動平均の傾きがプラス）
        try:
            df1 = df0.query('Close < MA10 and MA50 * 1.01 >= Close >= MA50 and Close.shift(1) > MA50.shift(1) * 1.01 and DIFF > 0.0005')
            if len(df1.index) > 0:
                buypoint_dt = df1.index[0]
                buypoint_p  = df1.loc[buypoint_dt, "Close"]
                reslist.append([50, buypoint_dt, df1.loc[buypoint_dt, "DIFF"]])
            else:
                pass
        except Exception as e:
            print(f"An error occurred: {e}")
            pass

    # 戻り値リストを日付で逆順ソート
        reslist = sorted(reslist, reverse=True, key=lambda x: x[1])  #[1]に注目してソート
        return reslist[0][0], reslist[0][1]

#---------------------------------------#
# ゴールデンクロス判定処理
#---------------------------------------#
    def GC_Check(self):

    # Dataframeをセット
        df0 = self.df
        start_dt = self.today - dt.timedelta(days=728)  # 104週前の日付
        df0 = df0.query('@start_dt <= index')           # データ範囲を絞り込み

    # 戻り値蓄積用リスト
        reslist = [["0",start_dt,0]]

    # ① MA50とMA150がゴールデンクロス（MA200の傾きがプラス）
        try:
            df1 = df0.query('MA50 > MA150 and MA50.shift(1) <= MA150.shift(1) and DIFF > 0.0005')
            if len(df1.index) > 0:
                gc_dt = df1.index[0]                      # MA50とMA150がGCした日
                buypoint_p = df1.loc[gc_dt, "Close"]
                reslist.append(["50-150",gc_dt,df1.loc[gc_dt,"DIFF"]])
            else:
                pass
        except Exception as e:
            print(f"An error occurred: {e}")
            pass

    # ② MA150とMA200がゴールデンクロス（MA200の傾きがプラス）
        try:
            df1 = df0.query('MA150 > MA200 and MA150.shift(1) <= MA200.shift(1) and DIFF > 0.0005')
            if len(df1.index) > 0:
                gc_dt = df1.index[0]                      # MA150とMA200がGCした日
                buypoint_p = df1.loc[gc_dt, "Close"]
                reslist.append(["150-200",gc_dt,df1.loc[gc_dt,"DIFF"]])
            else:
                pass
        except Exception as e:
            print(f"An error occurred: {e}")
            pass

    # 戻り値リストを日付で逆順ソート
        reslist = sorted(reslist, reverse=True, key=lambda x: x[1])  #[1]に注目してソート
        return reslist[0][0], reslist[0][1]

#---------------------------------------#
# 売りシグナル判定処理
#---------------------------------------#
    def ShortSign_Check(self):

    # Dataframeをセット
        df0 = self.df

        start_dt = self.today - dt.timedelta(days=455)  # 65週前の日付
        df0 = df0.query('@start_dt <= index')           # データ範囲を絞り込み
        rows = df0['High']

    #①期間の最高値日を取得
        if len(df0.index) > 0:
            max    = rows.max()
            idxmax = rows.idxmax()
            pass
        else:
            return 0, start_dt

    #②出来高を伴う50日移動平均割れ
        df1 = df0.query('index > @idxmax and Close < MA50 and Volume > MA_VOL')

    # STEP2判定
        if len(df1.index) > 0:
            under_ma50_dt = df1.index[0]
            neckline_p    = df1.loc[under_ma50_dt, "Close"]
            pass
        else:
            return 1, idxmax

    #③その後、3回以上50日移動平均を超える
        i = 0
        for i in range(3): # 3回ループ
            # 50日移動平均超え
            df1 = df0.query('index > @under_ma50_dt and Close > @neckline_p and Close > MA50')
            if len(df1.index) > 0:
                over_ma50_dt = df1.index[0]

                # 50日移動平均割れ
                df1 = df0.query('index > @over_ma50_dt and Close > @neckline_p and Close < MA50')
                if len(df1.index) > 0:
                    under_ma50_dt = df1.index[0]
                    continue
                else:
                    return 2, under_ma50_dt
                    break
            else:
                return 2, under_ma50_dt
                break
        else:
            pass

#    ④最後の上昇の出来高が少ない
#       print(int(df1.loc[over_ma50_dt, "Volume"]))
#       print(int(df1.loc[over_ma50_dt, "MA_VOL"]))

    # STEP4判定
        if df0.loc[over_ma50_dt, "Volume"] < df0.loc[over_ma50_dt, "MA_VOL"]:
            pass
        else:
            return 3, under_ma50_dt

    #⑤出来高を伴う下落
        df1 = df0.query('index > @over_ma50_dt and Close < MA50 and Volume > MA_VOL')

    # STEP5判定（出来高を伴う50日移動平均割れ）
        if len(df1.index) > 0:
            short_signal_dt = df1.index[0]
            return 5, short_signal_dt
        else:
            return 4, over_ma50_dt

#---------------------------------------#
# VCP1判定処理
#---------------------------------------#
    def VCP_Check1(self):

    # Dataframeを参照渡し
        df0 = self.df

    #①最高値を探す(90日以前)
        df1  = df0[: self.today - dt.timedelta(days=90)]
        rows = df1['High']

        if len(df1.index) > 0:
            max    = rows.max()
            idxmax = rows.idxmax()
        else:
            return 0, self.today

    #②最高値以降の最安値を探す（1番底）
        df1  = df0[idxmax : self.today]
        rows = df1['Low']
        min    = rows.min()
        idxmin = rows.idxmin()

    # 最安値値判定
        if (min / max >= 0.65) and (min / max <= 0.75):
            pass
        else:
            return 1, idxmax

    #③1番底以降の最高値（戻り高値）を探す
#   #　最高値日と最安値日の同数以上
#       days_div = abs(int((idxmin - idxmax).days)) # 中間日の日数
#       df2  = df1[idxmin + dt.timedelta(days=days_div) : self.today]
        df2  = df1[idxmin : self.today]
        rows = df2['High']

        if len(df2.index) > 0:
            max2 = rows.max()
            idxmax2 = rows.idxmax()
        else:
            return 2, idxmin

    # 戻り高値判定
        if (max2 / max >= 0.95) and (max2 / max <= 1):
            pass
        else:
            return 2, idxmin

    #④戻り高値以降の二番底を探す
        df2  = df1[idxmax2 : self.today]
        rows = df2['Low']
        min2 = rows.min()
        idxmin2 = rows.idxmin()

    # 二番底判定
        if (min2 / max2 >= 0.8) and (min2 / max2 <= 0.9):
            pass
        else:
            return 3, idxmin2

    #⑤2番底以降の最高値（戻り高値）を探す
        df2  = df1[idxmin2 : self.today]
        rows = df2['High']

        if len(df2.index) > 0:
            max3 = rows.max()
            idxmax3 = rows.idxmax()
        else:
            return 4, idxmin

    # 戻り高値判定
        if (max3 / max2 >= 0.95) and (max3 / max2 <= 1):
            pass
        else:
            return 4, idxmin

    #⑥戻り高値以降の三番底を探す
        df2  = df1[idxmax3 : self.today]
        rows = df2['Low']
        min3 = rows.min()
        idxmin3 = rows.idxmin()

    # 三番底判定
        if (min3 / max3 >= 0.9) and (min3 / max3 <= 0.97):
            pass
        else:
            return 5, idxmin2

    #⑦ピボット判定
        pivot_p1 = max3 * 0.99
        pivot_p2 = max3 * 1.01
        df2 = df1.query('index > @idxmin3 & @pivot_p1 <= High <= @pivot_p2')

    # STEP7判定
        if len(df2.index) > 0:
            pivot_dt1 = df2.index[0]
            pass
        else:
            return 6, idxmax3

    #⑧ピボットBreakout判定
        df2 = df1.query('index > @pivot_dt1 & High >= @max3')

    # STEP8判定
        if len(df2.index) > 0:
            pivot_dt2 = df2.index[0]
            return 8, pivot_dt2
        else:
            return 7, pivot_dt1

#---------------------------------------#
# VCP2判定処理
#---------------------------------------#
    def VCP_Check2(self):

    # Dataframeを参照渡し
        df0 = self.df

    #①最高値を探す(90日以前)
        df1  = df0[: self.today - dt.timedelta(days=90)]
        rows = df1['High']

        if len(df1.index) > 0:
            max    = rows.max()
            idxmax = rows.idxmax()
        else:
            return 0, self.today

    #②最高値以降の最安値を探す（1番底）
        df1  = df0[idxmax : self.today]
        rows = df1['Low']
        min    = rows.min()
        idxmin = rows.idxmin()

    # 最安値値判定
        if (min / max >= 0.65) and (min / max <= 0.75):
            pass
        else:
            return 1, idxmax

    #③1番底以降の最高値（戻り高値）を探す
        df2  = df1[idxmin : self.today]
        rows = df2['High']

        if len(df2.index) > 0:
            max2 = rows.max()
            idxmax2 = rows.idxmax()
        else:
            return 2, idxmin

    # 戻り高値判定
        if (max2 / max >= 0.95) and (max2 / max <= 1):
            pass
        else:
            return 2, idxmin

    #④一番底と戻り高値の間の二番底を探す
        days_div = abs(int(((idxmin - idxmax2).days)/2)) # 中間日の日数

        df2  = df1[idxmin + dt.timedelta(days=days_div) : idxmax2]
        rows = df2['Low']
        min2 = rows.min()
        idxmin2 = rows.idxmin()

    #⑤一番底と二番底の間の最高値（戻り高値）を探す
        df2  = df1[idxmin : idxmin2]
        rows = df2['High']

        if len(df2.index) > 0:
            max3 = rows.max()
            idxmax3 = rows.idxmax()
        else:
            return 4, idxmin

    # 戻り高値判定
        if (max3 / max >= 0.95) and (max3 / max <= 1) and (min2 / max3 >= 0.8) and (min2 / max3 <= 0.9):
            pass
        else:
            return 4, idxmin

    #⑥戻り高値以降の三番底を探す
        df2  = df1[idxmax2 : self.today]
        rows = df2['Low']
        min3 = rows.min()
        idxmin3 = rows.idxmin()

    # 三番底判定
        if (min3 / max2 >= 0.9) and (min3 / max2 <= 0.97):
            pass
        else:
            return 5, idxmin2

    #⑦ピボット判定
        pivot_p1 = max2 * 0.99
        pivot_p2 = max2 * 1.01
        df2 = df1.query('index > @idxmin3 & @pivot_p1 <= High <= @pivot_p2')

    # STEP7判定
        if len(df2.index) > 0:
            pivot_dt1 = df2.index[0]
            pass
        else:
            return 6, idxmax3

    #⑧ピボットBreakout判定
        df2 = df1.query('index > @pivot_dt1 & High >= @max3')

    # STEP8判定
        if len(df2.index) > 0:
            pivot_dt2 = df2.index[0]
            return 8, pivot_dt2
        else:
            return 7, pivot_dt1

#---------------------------------------#
# Double Bottom1判定処理
#---------------------------------------#
    def DoubleBottom_Check1(self):

    # Dataframeを参照渡し
        df0 = self.df

    # 補助線描画用リスト
        alist= []

    #①最高値を探す(60日以前)
        df1  = df0[: self.today - dt.timedelta(days=60)]
        rows = df1['High']

        if len(df1.index) > 0:
            max    = rows.max()
            idxmax = rows.idxmax()
            alist.append([idxmax, df0.loc[idxmax,"High"]])
        else:
            return 1, self.today, alist

    #②最高値以降の最安値を探す（1番底）
        df1  = df0[idxmax : self.today]
        rows = df1['Low']
        min    = rows.min()
        idxmin = rows.idxmin()
        alist.append([idxmin, df0.loc[idxmin,"Low"]])

    #③1番底以降の最高値（戻り高値）を探す
    #　最高値日と最安値日の同数以上
        days_div = int(abs(int((idxmin - idxmax).days)) * 0.67) # 中間日の日数×0.67

        df2  = df1[idxmin + dt.timedelta(days=days_div) : self.today]
        rows = df2['High']

        if len(df2.index) > 0:
            max2 = rows.max()
            idxmax2 = rows.idxmax()
        else:
            return 2, idxmin, alist

    # 戻り高値判定
        if (max2 / max >= 0.92) and (max2 / max <= 1):
            alist.append([idxmax2, df0.loc[idxmax2,"High"]])
        else:
            return 2, idxmin, alist

    #④戻り高値と以降の2番底を探す
    #　最高値日と最安値日の中間日以前
        days_div = abs(int(((idxmin - idxmax).days)/2)) # 中間日の日数
        df2  = df1[idxmax2 + dt.timedelta(days=days_div) : self.today]
#       df2  = df1[idxmax2 : self.today]

        if len(df2.index) > 0:
            rows    = df2['Low']
            min2    = rows.min()
            idxmin2 = rows.idxmin()
        else:
            return 3, idxmax2, alist

    # 二番底判定
        if (min / min2 >= 0.92) and (min / min2 <= 1):
            alist.append([idxmin2, df0.loc[idxmin2,"Low"]])
        else:
            return 3, idxmin2, alist

    #⑤ピボット判定
        pivot_p = max2 * 0.98
        df2 = df0.query('index > @idxmin2 & High >= @pivot_p')

    # STEP5判定
        if len(df2.index) > 0:
            pivot_dt1 = df2.index[0]
            alist.append([pivot_dt1, df0.loc[pivot_dt1,"High"]])
        else:
            return 4, idxmax2, alist

    #⑥ピボットBreakout判定
        df2 = df0.query('index >= @pivot_dt1 & High >= @max2')

    # STEP6判定
        if len(df2.index) > 0:
            pivot_dt2 = df2.index[0]
            alist.append([pivot_dt2, df0.loc[pivot_dt2,"High"]])
            return 6, pivot_dt2, alist
        else:
            return 5, pivot_dt1, alist

#---------------------------------------#
# Double Bottom2判定処理
#---------------------------------------#
    def DoubleBottom_Check2(self):

    # Dataframeを参照渡し
        df0 = self.df

    # 補助線描画用リスト
        alist= []

    #①最高値を探す(60日以前)
        df1  = df0[: self.today - dt.timedelta(days=60)]
        rows = df1['High']

        if len(df1.index) > 0:
            max    = rows.max()
            idxmax = rows.idxmax()
            alist.append([idxmax, df0.loc[idxmax,"High"]])
        else:
            return 1, self.today, alist

    #②最高値以降の最安値を探す
        df1  = df0[idxmax : self.today]
        rows = df1['Low']
        min    = rows.min()
        idxmin = rows.idxmin()
        alist.append([idxmin, df0.loc[idxmin,"Low"]])

    #③最高値と最安値の間の1番底を探す
    #　最高値日と最安値日の中間日以前
        days_div = abs(int(((idxmin - idxmax).days)/2)) # 中間日の日数

        df2  = df1[idxmax : idxmax + dt.timedelta(days=days_div)]
        rows = df2['Low']
        min2 = rows.min()
        idxmin2 = rows.idxmin()

    # 一番底判定
        if (min / min2 >= 0.92) and (min / min2 <= 1):
            alist.append([idxmin2, df0.loc[idxmin2,"Low"]])
        else:
            return 2, idxmin, alist

    #④1番底以降の最高値（戻り高値）を探す

        df2  = df1[idxmin2 : idxmin]
        rows = df2['High']
        max2 = rows.max()
        idxmax2 = rows.idxmax()

    # 戻り高値判定
        if (max2 / max >= 0.92) and (max2 / max <= 1):
            alist.append([idxmax2, df0.loc[idxmax2,"High"]])
        else:
            return 3, idxmin2, alist

    #⑤ピボット判定
        pivot_p = max2 * 0.98
        df2 = df0.query('index > @idxmin & High >= @pivot_p')

    # STEP5判定
        if len(df2.index) > 0:
            pivot_dt1 = df2.index[0]
            alist.append([pivot_dt1, df0.loc[pivot_dt1,"High"]])
        else:
            return 4, idxmax2, alist

    #⑥ピボットBreakout判定
        df2 = df0.query('index >= @pivot_dt1 & High >= @max2')

    # STEP6判定
        if len(df2.index) > 0:
            pivot_dt2 = df2.index[0]
            alist.append([pivot_dt2, df0.loc[pivot_dt2,"High"]])
            return 6, pivot_dt2, alist
        else:
            return 5, pivot_dt1, alist

#---------------------------------------#
# カップウィズハンドル判定処理
#---------------------------------------#
    def Cup_with_Handle_Check(self):

    # Dataframeを参照渡し
        df0 = self.df

    # 補助線描画用リスト
        alist= []

    # ダミー用戻り値
        dummy_dt = self.today

    #①カップの開始
    #　期間の最安値日を取得
        rows = df0['Low']
        if len(df0.index) > 0:
            min    = rows.min()
            idxmin = rows.idxmin()
#           alist.append((idxmin, df0.loc[idxmin,"Low"]))
        else:
            return 0, dummy_dt, alist

    #②カップの頂点
    #　期間の最安値日以降、直近30日以前の最高値が最安値の1.3倍以上
        maxlim_dt = self.today - dt.timedelta(days=30)
        df1  = df0[idxmin : maxlim_dt]
    #   df1  = df0[idxmin : self.today]
        if len(df1.index) > 0:
            rows = df1['High']
            max    = rows.max()
            idxmax = rows.idxmax()
            alist.append((idxmax, df0.loc[idxmax,"High"]))
        else:
            return 1, dummy_dt, alist

    # STEP2判定
        if max > min*1.3:
            pass
        else:
            return 1, idxmin, alist

    #③ベースの形成
    #　最高値から12～33%下落
        df1 = df0[idxmax : self.today]

    # ベース価格のレンジ
        base_p1 = max * 0.67
        base_p2 = max * 0.88

        df2 = df1.query('@base_p1 <= Close <= @base_p2')

    # STEP3判定
        if len(df2.index) > 0:
            base_sdt = df2.index[0]                # ベース開始日
            base_edt = df2.index[-1]               # ベース終了日
            base_len = (base_edt - idxmax).days    # ベース構成日数

            # ベースの平均値を計算
            base_avg = df2.Close.mean()

            # ベースの標準偏差を計算
            base_std = df2.Close.std()

            # 標準偏差÷平均値を計算
            base_rate = base_std / base_avg

            # ベースの最安値、最高値、最安日を取得
            df1 = df0[base_sdt : base_edt]
            base_min = df1['Close'].min()
            base_max = df1['Close'].max()
            base_bdt = df1['Close'].idxmin()

            # ベースの中間日を取得
            base_mdt = base_sdt + dt.timedelta(days=int(base_len/2))

            # ベース構成日数(最高値日から7～65週間)とベースの値幅約5%
            if (base_len >= 49) and (base_len <= 455) and (base_rate <= 0.05) and (base_min >= base_p1) and (base_max <= base_p2):
                alist.append((base_sdt, df0.loc[base_sdt,"Close"])) # ベースの開始
                alist.append((base_bdt, df0.loc[base_bdt,"Low"]))   # ベースの最安
                alist.append((base_mdt, base_avg))                  # ベースの平均
                alist.append((base_edt, df0.loc[base_edt,"Close"])) # ベースの終了
            else:
                return 2, idxmax, alist
        else:
            return 2, idxmax, alist

    #④カップの形成
    #　最高値の±5%まで上昇
        cup_p1 = max * 0.95
        cup_p2 = max * 1.05

    # カップ右の構成期間(最高値から7～65週間)
        base_edt1 = idxmax + dt.timedelta(days=49)     # 7週間後
        base_edt2 = idxmax + dt.timedelta(days=455)    # 65週間後
        df2 = df0.query('index >= @base_edt & @base_edt1 <= index <= @base_edt2 & @cup_p1 <= High')

    # STEP4 and 5判定
        if len(df2.index) > 0:
            cup_edt = df2.index[0]                        # カップ形成日（仮）

            # ハンドル部分の構成期間
            handle_edt1 = cup_edt                         # カップ形成日
            handle_edt2 = cup_edt + dt.timedelta(days=60) # カップ形成日から2ヵ月後

            # 期間中の高値
            df2 = df0.query('@handle_edt1 <= index <= @handle_edt2')
            rows      = df2['High']
            handle_p0 = rows.max()
            cup_edt   = rows.idxmax()                     # カップ形成日を再セット

            # 期間を再セット
            handle_edt1 = cup_edt + dt.timedelta(days=5)  # カップ形成日から1週間
            handle_edt2 = cup_edt + dt.timedelta(days=60) # カップ形成日から2ヵ月後

            # ハンドル部分の価格
            handle_p1 = handle_p0 * 0.88  # ハンドル下限
            handle_p2 = handle_p0 * 0.95  # ハンドル上限

        # 1～2週間後に5～12%下落があり、かつ50日週移動平均線より上
            df3 = df0.query('@handle_edt1 <= index <= @handle_edt2 & @handle_p1 <= Low <= @handle_p2 & MA50 <= Close')

        # 下落がなければ、期間中の高値がpivot(STEP4)
            if len(df3.index) == 0:
                pvt_p   = handle_p0
                # カップの高さの判定
                if pvt_p > cup_p2:
                    return 3, base_sdt, alist
                else:
                    alist.append((cup_edt, df0.loc[cup_edt,"High"]))
                    return 4, cup_edt, alist

        # ⑤下落があれば、安値前の高値がpivot、安値がハンドル(STEP5)
            else:
                # ハンドル部分
                rows = df3['Low']
                cwh_dt = rows.idxmin()

                # カップの高値
                pvt_p   = handle_p0

                alist.append((cup_edt, df0.loc[cup_edt,"High"]))  # カップの終了日をチャートに追加
                alist.append((cwh_dt, df0.loc[cwh_dt,"Low"]))     # ハンドルの形成日をチャートに追加
        else:
            return 3, base_sdt, alist

    #⑥ピボット判定
    #　判定期間をセット
        cwh_dtx = cwh_dt + dt.timedelta(days=30)  # カップ形成日から約1か月

    #　直近価格がピボットポイントを超える
        df2 = df0.query('@cwh_dt < index < @cwh_dtx & High >= @pvt_p')

    # STEP6判定
        if len(df2.index) > 0:
            pvt_dt = df2.index[0]
            alist.append((pvt_dt, df0.loc[pvt_dt,"High"]))
            return 6, pvt_dt, alist
        else:
            return 5, cwh_dt, alist

#---------------------------------------#
# フラットベース判定処理
#---------------------------------------#
    def FlatBase_Check(self):

    # Dataframeを参照渡し
        df0 = self.df

    # 補助線描画用リスト
        alist= []

    # ダミー用戻り値
        dummy_dt = self.today

    #①ベースの開始
    #　期間の最安値日を取得
        rows = df0['Low']
        if len(df0.index) > 0:
            min    = rows.min()
            idxmin = rows.idxmin()
#           alist.append((idxmin, df0.loc[idxmin,"Low"]))
        else:
            return 0, dummy_dt, alist

    #②ベースの頂点
    #　期間の最安値日以降、直近の最高値が最安値の1.2倍以上
        maxlim_dt = self.today - dt.timedelta(days=self.outPeriod)
        df1  = df0[idxmin : maxlim_dt]
        if len(df1.index) > 0:
            rows = df1['High']
            max    = rows.max()
            idxmax = rows.idxmax()
            alist.append((idxmax, df0.loc[idxmax,"High"]))
        else:
            return 1, dummy_dt, alist

    # STEP2判定
        if max > min*1.2:
            pass
        else:
            return 1, idxmin, alist

    #③ベースの形成
    #　最高値から5～15%下落
        df1 = df0[idxmax : self.today]

    # ベース価格のレンジ
        base_p1 = max * 0.85
        base_p2 = max * 0.95

        df2 = df1.query('@base_p1 <= Close <= @base_p2')

    # STEP3判定
        if len(df2.index) > 0:
            base_sdt = df2.index[0]                # ベース開始日
            base_edt = df2.index[-1]               # ベース終了日
            base_len = (base_edt - idxmax).days    # ベース構成日数

            # ベースの最安値、最高値、最安日を取得
            df1 = df0[base_sdt : base_edt]
            base_min = df1['Close'].min()
            base_max = df1['Close'].max()
            base_bdt = df1['Close'].idxmin()

            # ベース構成日数(最高値日から約4～8週間)と最安値が高値-15%を下回らない
            if (base_len >= 28) and (base_len <= 56) and (base_min >= base_p1) and (base_max <= base_p2):
                alist.append((base_sdt, df0.loc[base_sdt,"Close"])) # ベースの開始
                alist.append((base_bdt, df0.loc[base_bdt,"Low"]))   # ベースの最安
                alist.append((base_edt, df0.loc[base_edt,"Close"])) # ベースの終了
            else:
                return 2, idxmax, alist
        else:
            return 2, idxmax, alist

    #④ピボット判定
    #　直近価格がピボットポイントを超える
        df2 = df0.query('@base_edt < index & High >= @max')

    # STEP4判定
        if len(df2.index) > 0:
            pvt_dt = df2.index[0]
            alist.append((pvt_dt, df0.loc[pvt_dt,"High"]))
            return 4, pvt_dt, alist
        else:
            return 3, base_edt, alist

#---------------------------------------#
# O'Neil/Minervini流チャート判定
#---------------------------------------#
    def ON_Minervini_Check(self):
        # 定数の設定
        base_weeks_min = 7
        base_weeks_max = 65
        multiplier_min = 2.0
        multiplier_max = 3.0
        vol_reduction  = 0.3

        # Dataframeを複製
        df0 = self.df.copy()

        # 補助線描画用リスト
        alist = []

        # ベース期間を日付に変換
        base_length_min = dt.timedelta(weeks=base_weeks_min)
        base_length_max = dt.timedelta(weeks=base_weeks_max)

        # 直近の高値の日付を取得
        try:
            recent_max_date = df0['Close'].idxmax()
        except:
            return 0, None, alist

        # 直近の高値の日付が範囲外の場合は終了
        base_duration = df0.index[-1] - recent_max_date
        if base_length_min <= base_duration <= base_length_max:
            return 0, None, alist

        # 直近の高値の日付以降のデータに絞る
        df0 = df0.loc[recent_max_date:]

        # ボラティリティ調整による動的な価格下落を検出
        price_volatility = df0['Close'].pct_change().std()
        dynamic_drop_min = price_volatility * multiplier_min
        dynamic_drop_max = price_volatility * multiplier_max

        # 直近高値のローリング
        recent_max = df0['Close'].rolling(window=self.ma_mid).max()
#       print(f"Price Volatility: {price_volatility}")
#       print(f"Dynamic Drop Min: {dynamic_drop_min}")
#       print(f"Dynamic Drop Max: {dynamic_drop_max}")

        # 動的しきい値によるベースマスク
        base_mask = (
            (df0['Close'] <= recent_max * (1 - dynamic_drop_min)) &
            (df0['Close'] >= recent_max * (1 - dynamic_drop_max))
        )
        base_periods = df0[base_mask]

#       print(f"Base Periods Count: {len(base_periods)}")
        if not base_periods.empty:
            base_start_date = base_periods.index[0]
            base_end_date   = base_periods.index[-1]

            # ベース期間内の最高値
            recent_max_date = df0.loc[base_start_date:base_end_date, 'Close'].idxmax()

            # 最高値の位置を検証
            if not (base_start_date <= recent_max_date <= base_end_date):
                return 0, None, alist

            # ベース期間を評価
            base_duration = base_end_date - recent_max_date
            if not (base_length_min <= base_duration <= base_length_max):
                return 0, None, alist

            # ベース期間の最安値
            base_min_date  = df0.loc[recent_max_date:base_end_date, 'Close'].idxmin()
            base_min_value = df0.loc[base_min_date, "Close"]

            # 出来高分析
            # 直近の出来高平均と過去の出来高平均を比較
            recent_volume   = df0['Volume'].loc[recent_max_date:base_end_date].rolling(window=self.ma_short).mean()
            previous_volume = df0['Volume'].loc[:recent_max_date].rolling(window=self.ma_mid).mean().iloc[-1]

            # 直近の出来高減少
            volume_reduction_ratio = (previous_volume - recent_volume.mean()) / previous_volume

            # トレンド分析の改善
            long_term_ma = df0['Close'].rolling(window=self.ma_long).mean()
            trend_slope = long_term_ma.diff()

            # 状況の総合的な確認
            condition_checks = [
                volume_reduction_ratio > vol_reduction,        # 出来高が減少
                trend_slope.iloc[-1] > 0,                      # 200日移動平均線の傾きがプラス
                df0['Close'].iloc[-1] > long_term_ma.iloc[-1]  # 現在の株価が200日移動平均線を上回っている
            ]

            # 条件を満たす場合の処理
            if all(condition_checks):
                # 補助線描画用リストに追加
                alist.append((recent_max_date, df0.loc[recent_max_date, "Close"]))  # ベースの開始
                alist.append((base_min_date, base_min_value))                       # ベースの最安値
                alist.append((base_end_date, df0.loc[base_end_date, "Close"]))      # ベースの終了

                return 1, base_end_date, alist

        # 条件に合わない場合は0を返す
        return 0, None, alist

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
        df = pd.read_csv(doc, index_col=0, on_bad_lines='skip')
        df = df.dropna(how='all')                       # 欠損値を除外
        # インデックスを強制的にDatetimeIndexに変換し、タイムゾーンをUTCに統一
        df.index = pd.to_datetime(df.index, utc=True)

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
            if info != ["-","-","-","-","-"]:  # infoがデフォルト値（全部"-"）でなければCSV出力
                outTxt = str(res[1].date()) + "," + strLabel + ",\"" + self.strTicker + "\",\"" + info[1] + "\",\"" + info[2] + "\"," + info[4] + "," + str(ud_ratio2) + "," + str(ud_ratio1) + ",\"" + ud_mark + "\",\"" + info[3] + "\",\"" + str(round(df0['Close'].iloc[-1], 2)) + "\"\n"
                print("  Name   : " + info[1])
                print("  Sector : " + info[2])
                print("  UDVR   : " + ud_val + "  " + ud_mark)
                self.w.write(outTxt)
                self.w.flush()

        return
