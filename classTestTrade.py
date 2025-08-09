# coding: UTF-8

# Googleドライブのライブラリを指定(for Google Colab)
import sys
sys.path.append('/content/drive/MyDrive/Colab Notebooks/my-modules')

import os, fnmatch
import pandas as pd
import datetime as dt
import time, datetime
import yfinance as yf
from classDrawChart import DrawChart

#---------------------------------------#
# 株価データ分析クラス
#---------------------------------------#
class TestTrade():

#---------------------------------------#
# コンストラクタ
#---------------------------------------#
    def __init__(self, out_path, ma_short, ma_mid, ma_s_long, ma_long, rs_csv1, rs_csv2, txt_path):
        
        # 移動平均の期間をセット
        self.ma_short   = ma_short
        self.ma_mid     = ma_mid
        self.ma_s_long  = ma_s_long
        self.ma_long    = ma_long
        
        # 重複出力回避用変数
        self.prevTicker    = "----"
        self.prevshortName = '----'
        self.prevsector    = '----'
        self.prevLabel     = "N/A"
        self.prevDate      = dt.datetime.strptime('1999-01-01 00:00:00', '%Y-%m-%d %H:%M:%S')
        
        # 株価参照用DataFrame(空箱)
        self.df_ref = pd.DataFrame()
        
        # 今日の日付をセット
        self.today = dt.datetime.now()
#       self.start_dt = self.today - dt.timedelta(days=455)  # 65週前の日付
        self.start_dt = self.today - dt.timedelta(days=728)  # 104週前の日付
        
        # チャート出力クラスの作成
        self.chart = DrawChart(self.ma_short, self.ma_mid, self.ma_s_long, self.ma_long, rs_csv1, rs_csv2, txt_path)
        
        # ファイルの存在チェック
        is_file = os.path.isfile(out_path)
        if is_file == True:
            self.w = open(out_path, mode="a", encoding="CP932", errors="ignore")
        else:
            # 出力ファイルの作成
            self.w = open(out_path, mode="w", encoding="CP932", errors="ignore")
            # ファイルのヘッダー出力
            self.w.write("\"ティッカー\",\"タイプ\",\"会社名\",\"セクター\",\"判定日\",\"翌日寄値\",\"30日高値\",\"判定\"\n")
            self.w.flush()

#---------------------------------------#
# デストラクタ
#---------------------------------------#
    def __del__(self):
        # 出力ファイルを閉じる
        self.w.close()

#------------------------------------------------#
# トレンドテンプレート判定処理スタート（メイン）
#------------------------------------------------#
    def isTrendTemplete(self, doc):
    # ティッカーの処理
        strBaseName = os.path.splitext(os.path.basename(doc))[0]
        if (strBaseName[-2:] == "-X"):
            strTicker = strBaseName[:-2]
        else:
            strTicker = strBaseName

    # CSVファイルの読み込み
        self.df_ref = self.CSV_GetDF(doc)

    # Dataframeの範囲(END)を動かしながらループさせる
        l = len(self.df_ref) # レコード件数
        
        m = l - self.ma_s_long # ma_s_long件は固定、変動させる件数を求める
        print('REC CNT: l = {0}／m = {1}'.format(l, m))
        
        if m < 0:            # 0未満の場合は1をセット
            m = 1
        
        # カウンタがmになるまでループ
        i = 0
        for i in range(m):
            df1 = self.df_ref.head(self.ma_s_long + i) # dfの先頭からma_s_long+i件を取得
#           print(df1)
            
            # 処理呼び出し
            print('<-- Trend Templete -->')
            res = self.TrendTemplete_Check(df1)
            if (res[0] >= 7):
                self.isBuySign(df1, strTicker, strBaseName)  # トレンドテンプレートの場合、買いサインの判定を呼び出す

#------------------------------------------------#
# トレンドテンプレート判定処理スタート（全件チャート出力）
#------------------------------------------------#
    def isTrendTempleteAll(self, doc):
    # ティッカーの処理
        strBaseName = os.path.splitext(os.path.basename(doc))[0]
        if (strBaseName[-2:] == "-X"):
            strTicker = strBaseName[:-2]
        else:
            strTicker = strBaseName

    # CSVファイルの読み込み
        self.df_ref = self.CSV_GetDF(doc)

    # 処理呼び出し
        print('<-- Trend Templete -->')
        res = self.TrendTemplete_Check(self.df_ref)
        if res[0] >= 7:
            strLabel = "trend templete"
            self.writeFlles(strTicker, strBaseName, res, strLabel)  # CSV、チャート書き込み呼び出し

#------------------------------------------------#
# 買いサイン判定処理スタート（メイン）
#------------------------------------------------#
    def isBuySign(self, df1, strTicker, strBaseName):

        # Cup with Handle判定
        print('<-- Cup with Handle -->')
        res = self.Cup_with_Handle_Check(df1)
        if res[0] >= 4:
            strLabel = "cup with handle(" + str(res[0]) + ")"
            self.writeFlles(strTicker, strBaseName, res, strLabel)  # CSV、チャート書き込み呼び出し
        else:
            # VCP1判定
            print('<-- VCP 1 -->')
            res = self.VCP_Check1(df1)
            if res[0] >= 7:
                strLabel = "vcp1(" + str(res[0]) + ")"
                self.writeFlles(strTicker, strBaseName, res, strLabel)  # CSV、チャート書き込み呼び出し
            else:
                # VCP2判定
                print('<-- VCP 2 -->')
                res = self.VCP_Check2(df1)
                if res[0] >= 7:
                    strLabel = "vcp2(" + str(res[0]) + ")"
                    self.writeFlles(strTicker, strBaseName, res, strLabel)  # CSV、チャート書き込み呼び出し
                else:
                    # Double Bottom1判定
                    print('<-- Double Bottom 1 -->')
                    res = self.DoubleBottom_Check1(df1)
                    if res[0] >= 5:
                        strLabel = "double bottom1(" + str(res[0]) + ")"
                        self.writeFlles(strTicker, strBaseName, res, strLabel)  # CSV、チャート書き込み呼び出し
                    else:
                        # Double Bottom2判定
                        print('<-- Double Bottom 2 -->')
                        res = self.DoubleBottom_Check2(df1)
                        if res[0] >= 5:
                            strLabel = "double bottom2(" + str(res[0]) + ")"
                            self.writeFlles(strTicker, strBaseName, res, strLabel)  # CSV、チャート書き込み呼び出し
        print('--')
        return

#------------------------------------------------#
# 買いサイン判定処理スタート（グランビルの法則）
#------------------------------------------------#
    def isGranville(self, doc):
    # ティッカーの処理
        strBaseName = os.path.splitext(os.path.basename(doc))[0]
        if (strBaseName[-2:] == "-X"):
            strTicker = strBaseName[:-2]
        else:
            strTicker = strBaseName

    # CSVファイルの読み込み
        self.df_ref = self.CSV_GetDF(doc)

    # Dataframeの範囲(END)を動かしながらループさせる
        l = len(self.df_ref) # レコード件数
        
        m = l - self.ma_s_long # ma_s_long件は固定、変動させる件数を求める
        if m < 0:            # 0未満の場合は0をセット
            m = 0
        
        # カウンタがmになるまでループ
        for i in range(m):
            df1 = self.df_ref.head(self.ma_s_long + i) # dfの先頭からma_s_long+i件を取得
            self.today = df1.index[-1]        # 日付を再セット

        # 処理呼び出し
            print('<-- Buy Sign -->')
            res = self.BuySign_Check(df1)
            if (res[0] == 1) or (res[0] == 3):
                strLabel = "buy sign(" + str(res[0]) + ")"
                self.writeFlles(strTicker, strBaseName, res, strLabel)  # CSV、チャート書き込み呼び出し

        print('--')
        return

#------------------------------------------------#
# 売りサイン判定処理スタート（メイン）
#------------------------------------------------#
    def isShortSign(self, doc):
    # ティッカーの処理
        strBaseName = os.path.splitext(os.path.basename(doc))[0]
        if (strBaseName[-2:] == "-X"):
            strTicker = strBaseName[:-2]
        else:
            strTicker = strBaseName

    # 処理呼び出し
        print('<-- Short Sign -->')
        res = self.ShortSign_Check(self.CSV_GetDF(doc))

    # 出力ファイルへ書き込み（ステータスが5以上かつ10日以内のの場合）
        if res[0] >= 5:
                strLabel = "short sign"
                self.writeFlles(strTicker, strBaseName, res, strLabel) # CSV、チャート書き込み呼び出し
        print('--')
        return

#---------------------------------------#
# トレンドテンプレート判定処理
#---------------------------------------#
    def TrendTemplete_Check(self, df):

        df0 = df.copy()

    # 直近の日付、終値
        if len(df0.index) > 0:
            idxtoday = df0.index[-1]
            close_p  = df0.loc[idxtoday, 'Close']
            print('直近日付:{0}／終値:{1}'.format(idxtoday.date(), round(close_p,2)))
        else:
            print('STEP1／NG orz')
            return 0, self.start_dt, df0

    # ① 終値が150日と200日移動平均線より上
        if (close_p >= df0.loc[idxtoday, 'MA150']) and (close_p >= df0.loc[idxtoday, 'MA200']):
            print('STEP1／OK!! MA150,MA200超:@{0}'.format(round(close_p,2)))
        else:
            print('STEP1／NG orz')
            return 0, self.start_dt, df0

    # ② 150日移動平均線が200日移動平均線より上
        if df0.loc[idxtoday, 'MA150'] >= df0.loc[idxtoday, 'MA200']:
            print('STEP2／OK!! MA150 >= MA200')
        else:
            print('STEP2／NG orz')
            return 1, self.start_dt, df0

    # ③ 200日移動平均線が少なくとも1ヵ月以上上昇トレンド
        if df0.loc[idxtoday, 'DIFF'] > 0:
            print('STEP3／OK!! DIFF:{0}'.format(round(df0.loc[idxtoday, 'DIFF'],5)))
        else:
            print('STEP3／NG orz')
            return 2, self.start_dt, df0

    # ④ 50日移動平均線が150日、200日移動平均線より上
        if (df0.loc[idxtoday, 'MA50'] >= df0.loc[idxtoday, 'MA150']) and (df0.loc[idxtoday, 'MA50'] >= df0.loc[idxtoday, 'MA200']):
            print('STEP4／OK!! MA50 >= MA150 & MA50 >= MA200')
        else:
            print('STEP4／NG orz')
            return 3, self.start_dt, df0

    # ⑤ 現在の株価が50日移動平均線より上
        if close_p >= df0.loc[idxtoday, 'MA50']:
            print('STEP5／OK!! MA50超')
        else:
            print('STEP5／NG orz')
            return 4, self.start_dt, df0

    # ⑥ 現在の株価が52週安値より少なくとも30％高い
        start_dt52w = self.start_dt - dt.timedelta(days=365)  # 52週前の日付
        df1 = df0.query('@start_dt52w <= index')           # データ範囲を絞り込み
        
        rows   = df1['Low']
        min    = rows.min()
        idxmin = rows.idxmin()
        
        if close_p >= min * 1.3:
            print('STEP6／OK!! 52週安値:{0} 直近終値:{1}'.format(round(min,2), round(close_p,2)))
        else:
            print('STEP6／NG orz')
            return 5, self.start_dt, df0

    # ⑦ 現在の株価は52週高値から25％以内
        rows   = df0['High']
        max    = rows.max()
        idxmax = rows.idxmax()
        
        if close_p >= max * 0.75:
            print('STEP7／OK!! 52週高値:{0} 直近終値:{1}'.format(round(max,2), round(close_p,2)))
            print()
            return 7, idxtoday, df0
        else:
            print('STEP6／NG orz')
            return 6, self.start_dt, df0

#---------------------------------------#
# 買いシグナル判定処理
#---------------------------------------#
    def BuySign_Check(self, df):

    # 参照渡しでなく、コピーを作る
        df0 = df.copy()

    # 戻り値蓄積用リスト
        reslist = [[0,self.start_dt,0]]

    # 買い①：株価がMA200を超える（移動平均の傾きがプラス）
        df1 = df0.query('Close > MA200 and DIFF > 0.0001')

    # STEP1判定
        if len(df1.index) > 0:
            step1_dt   = df1.index[0]                    # df1の先頭の日付
            df2 = df0.query('index < @step1_dt').tail(1) # その前日の終値を探す
            step1_pd = df2.index[-1]                     # 前日の日付
            step1_pp = df2.loc[step1_pd, 'Close']        # 前日の終値の値
            step1_pm = df2.loc[step1_pd, 'MA200']        # 前日のMA200の値
            
            if step1_pp > step1_pm:                      # 前日もMA200より上ならNG
                print('STEP1／NG orz')
            else:
                buypoint_p = df1.loc[step1_dt, "Close"]
                print('STEP1／OK!! MA200超え日付:{0} @{1}'.format(step1_dt.date(), round(buypoint_p,2)))
                reslist.append([1,step1_dt,df1.loc[step1_dt,"DIFF"]])
        else:
            print('STEP1／NG orz')

    # 買い②：株価がMA200を下回る（移動平均の傾きがプラス）
        df1 = df0.query('Close < MA200 and DIFF > 0.0005')

    # STEP2判定
        if len(df1.index) > 0:
            step2_dt   = df1.index[0] # MA200を割った日
            buypoint_p = df1.loc[step2_dt, "Close"]
            
            print('STEP2／OK!! MA200割れ日付:{0} @{1}'.format(step2_dt.date(), round(buypoint_p,2)))
            reslist.append([2,step2_dt,df1.loc[step2_dt,"DIFF"]])
        else:
            print('STEP2／NG orz')

    # 買い③：株価がMA200上で反発（移動平均の傾きがプラス）
        df1 = df0.query('Close < MA10 and MA200 * 1.01 >= Close >= MA200 and DIFF > 0.0005')

    # STEP3判定
        if len(df1.index) > 0:
            step3_dt = df1.index[0] # MA200を超えた日
            
            df2 = df0.query('index < @step3_dt').tail(1) # その前日の終値を探す
            step3_pd = df2.index[-1]                     # 前日の日付
            step3_pp = df2.loc[step3_pd, 'Close']        # 前日の終値の値
            step3_pm = df2.loc[step3_pd, 'MA200']        # 前日のMA200の値
            
            if step3_pp < step3_pm:                      # 前日、MA200より下ならNG
                print('STEP3／NG orz')
            else:
                buypoint_p = df1.loc[step3_dt, "Close"]
                print('STEP3／OK!! MA200超え日付:{0} @{1}'.format(step3_dt.date(), round(buypoint_p,2)))
                reslist.append([3,step3_dt,df1.loc[step3_dt,"DIFF"]])
        else:
            print('STEP3／NG orz')

    # 買い④：株価がMA200を割って大きく下落（移動平均の傾きがプラス）
        df1 = df0.query('MA200 * 0.9 >= Close and DIFF > 0')

    # STEP4判定
        if len(df1.index) > 0:
            step4_dt   = df1.index[0] # MA200を超えた日
            buypoint_p = df1.loc[step4_dt, "Close"]
            
            print('STEP4／OK!! MA200割れ日付:{0} @{1}'.format(step4_dt.date(), round(buypoint_p,2)))
            reslist.append([4,step4_dt,df1.loc[step4_dt,"DIFF"]])
        else:
            print('STEP4／NG orz')

    # 戻り値リストを日付で逆順ソート
        reslist = sorted(reslist, reverse=True, key=lambda x: x[1])  #[1]に注目してソート
#       print(reslist)
        print('戻り値／Lv:{0}, Date:{1}, Diff:{2}'.format(reslist[0][0], reslist[0][1].date(), round(reslist[0][2],5)))
        return reslist[0][0], reslist[0][1], df0

#---------------------------------------#
# 売りシグナル判定処理
#---------------------------------------#
    def ShortSign_Check(self, df0):

    #①期間の最高値日を取得
        rows = df0['High']
        if len(df0.index) > 0:
            max    = rows.max()
            idxmax = rows.idxmax()
            print('STEP1／最高値: {0} 日付:{1}'.format(round(max, 2), idxmax.date()))
        else:
            print('STEP1／NG...orz')
            return 0, self.start_dt, df0

    #②出来高を伴う50日移動平均割れ
        df1 = df0.query('index > @idxmax and Close < MA50 and Volume > MA_VOL')

    # STEP2判定
        if len(df1.index) > 0:
            under_ma50_dt = df1.index[0]
            neckline_p    = df1.loc[under_ma50_dt, "Close"]
            print('STEP2／OK!! MA50割れ日付:{0} @{1}'.format(under_ma50_dt.date(), round(neckline_p,2)))
        else:
            print("STEP2／NG...orz")
            return 1, idxmax, df0

    #③その後、3回以上50日移動平均を超える
        i = 0
        for i in range(3): # 3回ループ
            # 50日移動平均超え
            df1 = df0.query('index > @under_ma50_dt and Close > @neckline_p and Close > MA50')
            if len(df1.index) > 0:
                over_ma50_dt = df1.index[0]
                print('STEP3／MA50越え日付({0}):{1}'.format(i, over_ma50_dt.date()))
                
                # 50日移動平均割れ
                df1 = df0.query('index > @over_ma50_dt and Close > @neckline_p and Close < MA50')
                if len(df1.index) > 0:
                    under_ma50_dt = df1.index[0]
                    continue
                else:
                    print("STEP3／NG...orz")
                    return 2, under_ma50_dt, df0
                    break
            else:
                print("STEP3／NG...orz")
                return 2, under_ma50_dt, df0
                break
        else:
            print('STEP3／OK!!')

#    ④最後の上昇の出来高が少ない
#       print(int(df1.loc[over_ma50_dt, "Volume"]))
#       print(int(df1.loc[over_ma50_dt, "MA_VOL"]))

    # STEP4判定
        if df0.loc[over_ma50_dt, "Volume"] < df0.loc[over_ma50_dt, "MA_VOL"]:
            print('STEP4／OK!! 出来高減少')
        else:
            print("STEP4／NG...orz")
            return 3, under_ma50_dt, df0

    #⑤出来高を伴う下落
        df1 = df0.query('index > @over_ma50_dt and Close < MA50 and Volume > MA_VOL')

    # STEP5判定（出来高を伴う50日移動平均割れ）
        if len(df1.index) > 0:
            short_signal_dt = df1.index[0]
            print('STEP5／OK!! 売りシグナル日付:{0}'.format(short_signal_dt.date()))
            return 5, short_signal_dt, df0
        else:
            print("STEP5／NG...orz")
            return 4, over_ma50_dt, df0

#---------------------------------------#
# VCP1判定処理
#---------------------------------------#
    def VCP_Check1(self, df0):

    #①最高値を探す(90日以前)
        df1  = df0[: self.today - dt.timedelta(days=90)]
        rows = df1['High']
        
        if len(df1.index) > 0:
            max    = rows.max()
            idxmax = rows.idxmax()
            print('STEP1／最高値: {0} 日付:{1}'.format(round(max, 2), idxmax.date()))
        else:
            print('STEP1／NG...orz')
            return 0, self.today, df0

    #②最高値以降の最安値を探す（1番底）
        df1  = df0[idxmax : self.today]
        rows = df1['Low']
        min    = rows.min()
        idxmin = rows.idxmin()
        print('STEP2／一番底: {0} 日付:{1}'.format(round(min, 2), idxmin.date()))

    # 最安値値判定
        if (min / max >= 0.65) and (min / max <= 0.75):
            print('STEP2／一番底：OK')
        else:
            print("STEP3／NG...orz")
            return 1, idxmax, df0

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
            print("STEP3／NG...orz : NO ROWS")
            return 2, idxmin, df0

#       print('STEP3／戻り高値1: {0} 日付:{1}'.format(round(max2, 2), idxmax2.date()))
    # 戻り高値判定
        if (max2 / max >= 0.95) and (max2 / max <= 1):
            print('STEP3／戻り高値1: {0} 日付:{1}'.format(round(max2, 2), idxmax2.date()))
        else:
            print("STEP3／NG...orz")
            return 2, idxmin, df0

    #④戻り高値以降の二番底を探す
        df2  = df1[idxmax2 : self.today]
        rows = df2['Low']
        min2 = rows.min()
        idxmin2 = rows.idxmin()

    # 二番底判定
        if (min2 / max2 >= 0.8) and (min2 / max2 <= 0.9):
            print('STEP4／ニ番底: {0} 日付:{1}'.format(round(min2, 2), idxmin2.date()))
        else:
            print("STEP4／NG...orz")
            return 3, idxmin2, df0

    #⑤2番底以降の最高値（戻り高値）を探す
        df2  = df1[idxmin2 : self.today]
        rows = df2['High']

        if len(df2.index) > 0:
            max3 = rows.max()
            idxmax3 = rows.idxmax()
        else:
            print("STEP5／NG...orz : NO ROWS")
            return 4, idxmin, df0

#       print('STEP5／戻り高値2: {0} 日付:{1}'.format(round(max3, 2), idxmax3.date()))
    # 戻り高値判定
        if (max3 / max2 >= 0.95) and (max3 / max2 <= 1):
            print('STEP5／戻り高値2: {0} 日付:{1}'.format(round(max3, 2), idxmax3.date()))
        else:
            print("STEP5／NG...orz")
            return 4, idxmin, df0

    #⑥戻り高値以降の三番底を探す
        df2  = df1[idxmax3 : self.today]
        rows = df2['Low']
        min3 = rows.min()
        idxmin3 = rows.idxmin()

    # 三番底判定
        if (min3 / max3 >= 0.9) and (min3 / max3 <= 0.97):
            print('STEP6／三番底: {0} 日付:{1}'.format(round(min3, 2), idxmin3.date()))
        else:
            print("STEP6／NG...orz")
            return 5, idxmin2, df0

    #⑦ピボット判定
        pivot_p1 = max3 * 0.99
        pivot_p2 = max3 * 1.01
        df2 = df1.query('index > @idxmin3 & @pivot_p1 <= High <= @pivot_p2')

    # STEP7判定
        if len(df2.index) > 0:
            pivot_dt1 = df2.index[0]
            print('STEP7／OK!! VCP形成日付:{0}'.format(pivot_dt1.date()))
        else:
            print("STEP7／NG...orz")
            return 6, idxmax3, df0

    #⑧ピボットBreakout判定
        df2 = df1.query('index > @pivot_dt1 & High >= @max3')

    # STEP8判定
        if len(df2.index) > 0:
            pivot_dt2 = df2.index[0]
            print('STEP8／OK!! VCP Breakout日付:{0}'.format(pivot_dt2.date()))
            return 8, pivot_dt2, df0
        else:
            print("STEP8／NG...orz")
            return 7, pivot_dt1, df0

#---------------------------------------#
# VCP2判定処理
#---------------------------------------#
    def VCP_Check2(self, df0):

    #①最高値を探す(90日以前)
        df1  = df0[: self.today - dt.timedelta(days=90)]
        rows = df1['High']
        
        if len(df1.index) > 0:
            max    = rows.max()
            idxmax = rows.idxmax()
            print('STEP1／最高値: {0} 日付:{1}'.format(round(max, 2), idxmax.date()))
        else:
            print('STEP1／NG...orz')
            return 0, self.today, df0

    #②最高値以降の最安値を探す（1番底）
        df1  = df0[idxmax : self.today]
        rows = df1['Low']
        min    = rows.min()
        idxmin = rows.idxmin()
        print('STEP2／一番底: {0} 日付:{1}'.format(round(min, 2), idxmin.date()))

    # 最安値値判定
        if (min / max >= 0.65) and (min / max <= 0.75):
            print('STEP2／一番底：OK')
        else:
            print("STEP3／NG...orz")
            return 1, idxmax, df0

    #③1番底以降の最高値（戻り高値）を探す
        df2  = df1[idxmin : self.today]
        rows = df2['High']

        if len(df2.index) > 0:
            max2 = rows.max()
            idxmax2 = rows.idxmax()
        else:
            print("STEP3／NG...orz : NO ROWS")
            return 2, idxmin, df0

    # 戻り高値判定
        if (max2 / max >= 0.95) and (max2 / max <= 1):
            print('STEP3／戻り高値1: {0} 日付:{1}'.format(round(max2, 2), idxmax2.date()))
        else:
            print("STEP3／NG...orz")
            return 2, idxmin, df0

    #④一番底と戻り高値の間の二番底を探す
        days_div = abs(int(((idxmin - idxmax2).days)/2)) # 中間日の日数

        df2  = df1[idxmin + dt.timedelta(days=days_div) : idxmax2]
        rows = df2['Low']
        min2 = rows.min()
        idxmin2 = rows.idxmin()

        print('STEP4／ニ番底: {0} 日付:{1}'.format(round(min2, 2), idxmin2.date()))

    #⑤一番底と二番底の間の最高値（戻り高値）を探す
        df2  = df1[idxmin : idxmin2]
        rows = df2['High']

        if len(df2.index) > 0:
            max3 = rows.max()
            idxmax3 = rows.idxmax()
        else:
            print("STEP5／NG...orz : NO ROWS")
            return 4, idxmin, df0

    # 戻り高値判定
        if (max3 / max >= 0.95) and (max3 / max <= 1) and (min2 / max3 >= 0.8) and (min2 / max3 <= 0.9):
            print('STEP5／戻り高値2: {0} 日付:{1}'.format(round(max3, 2), idxmax3.date()))
        else:
            print("STEP5／NG...orz")
            return 4, idxmin, df0

    #⑥戻り高値以降の三番底を探す
        df2  = df1[idxmax2 : self.today]
        rows = df2['Low']
        min3 = rows.min()
        idxmin3 = rows.idxmin()

    # 三番底判定
        if (min3 / max2 >= 0.9) and (min3 / max2 <= 0.97):
            print('STEP6／三番底: {0} 日付:{1}'.format(round(min3, 2), idxmin3.date()))
        else:
            print("STEP6／NG...orz")
            return 5, idxmin2, df0

    #⑦ピボット判定
        pivot_p1 = max2 * 0.99
        pivot_p2 = max2 * 1.01
        df2 = df1.query('index > @idxmin3 & @pivot_p1 <= High <= @pivot_p2')

    # STEP7判定
        if len(df2.index) > 0:
            pivot_dt1 = df2.index[0]
            print('STEP7／OK!! VCP形成日付:{0}'.format(pivot_dt1.date()))
        else:
            print("STEP7／NG...orz")
            return 6, idxmax3, df0

    #⑧ピボットBreakout判定
        df2 = df1.query('index > @pivot_dt1 & High >= @max3')

    # STEP8判定
        if len(df2.index) > 0:
            pivot_dt2 = df2.index[0]
            print('STEP8／OK!! VCP Breakout日付:{0}'.format(pivot_dt2.date()))
            return 8, pivot_dt2, df0
        else:
            print("STEP8／NG...orz")
            return 7, pivot_dt1, df0

#---------------------------------------#
# Double Bottom1判定処理
#---------------------------------------#
    def DoubleBottom_Check1(self, df0):

    #①最高値を探す(60日以前)
        df1  = df0[: self.today - dt.timedelta(days=60)]
        rows = df1['High']
        
        if len(df1.index) > 0:
            max    = rows.max()
            idxmax = rows.idxmax()
            print('STEP1／最高値: {0} 日付:{1}'.format(round(max, 2), idxmax.date()))
        else:
            print('STEP1／NG...orz')
            return 1, self.today, df0

    #②最高値以降の最安値を探す（1番底）
        df1  = df0[idxmax : self.today]
        rows = df1['Low']
        min    = rows.min()
        idxmin = rows.idxmin()
        print('STEP2／一番底: {0} 日付:{1}'.format(round(min, 2), idxmin.date()))

    #③1番底以降の最高値（戻り高値）を探す
    #　最高値日と最安値日の同数以上
        days_div = int(abs(int((idxmin - idxmax).days)) * 0.67) # 中間日の日数×0.67

        df2  = df1[idxmin + dt.timedelta(days=days_div) : self.today]
        rows = df2['High']

        if len(df2.index) > 0:
            max2 = rows.max()
            idxmax2 = rows.idxmax()
        else:
            print("STEP3／NG...orz : NO ROWS")
            return 2, idxmin, df0

    # 戻り高値判定
        if (max2 / max >= 0.92) and (max2 / max <= 1):
            print('STEP3／戻り高値: {0} 日付:{1}'.format(round(max2, 2), idxmax2.date()))
        else:
            print("STEP3／NG...orz")
            return 2, idxmin, df0

    #④戻り高値と以降の2番底を探す
        df2  = df1[idxmax2 : self.today]
        rows = df2['Low']
        min2 = rows.min()
        idxmin2 = rows.idxmin()

    # 二番底判定
        if (min / min2 >= 0.92) and (min / min2 <= 1):
            print('STEP4／ニ番底: {0} 日付:{1}'.format(round(min2, 2), idxmin2.date()))
        else:
            print("STEP4／NG...orz")
            return 3, idxmin2, df0


    #⑤ピボット判定
        pivot_p = max2 * 0.98
#       df2 = df1.query('index > @idxmin2 & @max2 >= High >= @pivot_p')
        df2 = df1.query('index > @idxmin2 & High >= @pivot_p')

    # STEP5判定
        if len(df2.index) > 0:
            pivot_dt1 = df2.index[0]
            print('STEP5／OK!! ダブルボトム形成日付:{0}'.format(pivot_dt1.date()))
        else:
            print("STEP5／NG...orz")
            return 4, idxmax2, df0

    #⑥ピボットBreakout判定
        df2 = df1.query('index > @pivot_dt1 & High >= @max2')

    # STEP6判定
        if len(df2.index) > 0:
            pivot_dt2 = df2.index[0]
            print('STEP6／OK!! ダブルボトム Breakout日付:{0}'.format(pivot_dt2.date()))
            return 6, pivot_dt2, df0
        else:
            print("STEP6／NG...orz")
            return 5, pivot_dt1, df0

#---------------------------------------#
# Double Bottom2判定処理
#---------------------------------------#
    def DoubleBottom_Check2(self, df0):
    

    #①最高値を探す(60日以前)
        df1  = df0[: self.today - dt.timedelta(days=60)]
        rows = df1['High']
        
        if len(df1.index) > 0:
            max    = rows.max()
            idxmax = rows.idxmax()
            print('STEP1／最高値: {0} 日付:{1}'.format(round(max, 2), idxmax.date()))
        else:
            print('STEP1／NG...orz')
            return 1, self.today, df0

    #②最高値以降の最安値を探す
        df1  = df0[idxmax : self.today]
        rows = df1['Low']
        min    = rows.min()
        idxmin = rows.idxmin()
        print('STEP2／最安値: {0} 日付:{1}'.format(round(min, 2), idxmin.date()))


    #③最高値と最安値の間の1番底を探す
    #　最高値日と最安値日の中間日以前
        days_div = abs(int(((idxmin - idxmax).days)/2)) # 中間日の日数

        df2  = df1[idxmax : idxmax + dt.timedelta(days=days_div)]
        rows = df2['Low']
        min2 = rows.min()
        idxmin2 = rows.idxmin()

    # 一番底判定
        if (min / min2 >= 0.92) and (min / min2 <= 1):
            print('STEP3／一番底: {0} 日付:{1}'.format(round(min2, 2), idxmin2.date()))
        else:
            print("STEP3／NG...orz")
            return 2, idxmin, df0

    #④1番底以降の最高値（戻り高値）を探す

        df2  = df1[idxmin2 : idxmin]
        rows = df2['High']
        max2 = rows.max()
        idxmax2 = rows.idxmax()

    # 戻り高値判定
        if (max2 / max >= 0.92) and (max2 / max <= 1):
            print('STEP4／戻り高値: {0} 日付:{1}'.format(round(max2, 2), idxmax2.date()))
        else:
            print("STEP4／NG...orz")
            return 3, idxmin2, df0

    #⑤ピボット判定
        pivot_p = max2 * 0.98
#       df2 = df1.query('index > @idxmin & @max2 >= High >= @pivot_p')
        df2 = df1.query('index > @idxmin & High >= @pivot_p')

    # STEP5判定
        if len(df2.index) > 0:
            pivot_dt1 = df2.index[0]
            print('STEP5／OK!! ダブルボトム形成日付:{0}'.format(pivot_dt1.date()))
        else:
            print("STEP5／NG...orz")
            return 4, idxmax2, df0

    #⑥ピボットBreakout判定
        df2 = df1.query('index > @pivot_dt1 & High >= @max2')

    # STEP6判定
        if len(df2.index) > 0:
            pivot_dt2 = df2.index[0]
            print('STEP6／OK!! ダブルボトム Breakout日付:{0}'.format(pivot_dt2.date()))
            return 6, pivot_dt2, df0
        else:
            print("STEP6／NG...orz")
            return 5, pivot_dt1, df0

#---------------------------------------#
# カップウィズハンドル判定処理
#---------------------------------------#
    def Cup_with_Handle_Check(self, df0):

    #①カップの開始
    #　期間の最安値日を取得
        rows = df0['Low']
        if len(df0.index) > 0:
            min    = rows.min()
            idxmin = rows.idxmin()
            print('STEP1／最安値: {0} 日付:{1}'.format(round(min, 2), idxmin.date()))
        else:
            print('STEP1／NG...orz  NO ROW')
            return 0, self.start_dt, df0

    #②カップの頂点
    #　期間の最安値日以降、直近60日以前の最高値が最安値の1.3倍以上
        maxlim_dt = self.today - dt.timedelta(days=60)
        df1  = df0[idxmin : maxlim_dt]
    #   df1  = df0[idxmin : self.today]
        if len(df1.index) > 0:
            rows = df1['High']
            max    = rows.max()
            idxmax = rows.idxmax()
            print('STEP2／最高値: {0} 日付:{1}'.format(round(max, 2), idxmax.date()))
        else:
            print('STEP2／NG...orz  NO ROW')
            return 1, self.start_dt, df0

    # STEP2判定
        if max > min*1.3:
            print("STEP2／OK!!")
        else:
            print("STEP2／NG...orz")
            return 1, idxmin, df0

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
            base_edt = df2.index[len(df2.index)-1] # ベース終了日
            base_len = (base_edt - idxmax).days    # ベース構成日数
            print('STEP3／ベース構成日数:{0}日({1} <--> {2})'.format(base_len, base_sdt.date(), base_edt.date()))
            
            # ベースの平均値を計算
            base_avg = df2.Close.mean()
            # print('STEP3／平均値:{0}'.format(base_avg))
            
            # ベースの標準偏差を計算
            base_std = df2.Close.std()
            # print('STEP3／標準偏差:{0}'.format(base_std))
            
            # 標準偏差÷平均値を計算
            base_rate = base_std / base_avg
            print('STEP3／平均値÷標準偏差:{0}'.format(round(base_rate,5)))
            
            # ベース構成日数(最高値日から7～65週間)とベースの値幅約5%
            if (base_len >= 49) and (base_len <= 455) and (base_rate <= 0.05):
                print('STEP3／OK!! ベース形成')
            else:
                print("STEP3／NG...orz ベース構成NG")
                return 2, idxmax
        else:
            print("STEP3／NG...orz")
            return 2, idxmax, df0


    #④カップの形成
    #　最高値の-5～+5%まで上昇
        cup_p1 = max * 0.95
        cup_p2 = max * 1.05

    # カップ右の構成期間(最高値から7～65週間)
        base_edt1 = idxmax + dt.timedelta(days=49)     # 7週間後
        base_edt2 = idxmax + dt.timedelta(days=455)    # 65週間後
#       df2 = df0.query('index >= @base_edt & @base_edt1 <= index <= @base_edt2 & @cup_p1 <= High <= @cup_p2')
        df2 = df0.query('index >= @base_edt & @base_edt1 <= index <= @base_edt2 & @cup_p1 <= High')

    # STEP4 and 5判定
        if len(df2.index) > 0:
            cup_edt = df2.index[0]                        # カップ形成日（仮）

            # ハンドル部分の構成期間
            handle_edt1 = cup_edt                         # カップ形成日
            handle_edt2 = cup_edt + dt.timedelta(days=14) # カップ形成日から約2週間後
            
            # 期間中の高値
            df2 = df0.query('@handle_edt1 <= index <= @handle_edt2')
            rows      = df2['High']
            handle_p0 = rows.max()
            cup_edt   = rows.idxmax()                     # カップ形成日を再セット

            # 期間を再セット
            handle_edt1 = cup_edt + dt.timedelta(days=5)  # カップ形成日から約1週間
            handle_edt2 = cup_edt + dt.timedelta(days=14) # カップ形成日から約2週間後

            # ハンドル部分の価格
            handle_p1 = handle_p0 * 0.88  # ハンドル下限
            handle_p2 = handle_p0 * 0.95  # ハンドル上限
            
        # 1～2週間後に5～12%下落があり、かつ50日週移動平均線より上
            df3 = df0.query('@handle_edt1 <= index <= @handle_edt2 & @handle_p1 <= Close <= @handle_p2 & MA50 <= Close')

        # 下落がなければ、期間中の高値がpivot(STEP4)
            if len(df3.index) == 0:
                pvt_p   = handle_p0
                # カップの高さの判定
                if pvt_p > cup_p2:
                    print("STEP4／NG...Cup is TOO HIGH")
                    return 3, base_sdt, df0
                else:
                    print('STEP4／OK!! カップ形成日付:{0}'.format(cup_edt.date()))
                    return 4, cup_edt, df0
                
        # ⑤下落があれば、安値前の高値がpivot、安値がハンドル(STEP5)
            else:
                # ハンドル部分
                rows = df3['Low']
                cwh_dt = rows.idxmin()
                
                # カップの高値
                pvt_p   = handle_p0
                
                print('STEP5／OK!! カップウィズハンドル日付:{0}'.format(cwh_dt.date()))
        else:
            print("STEP4／NG...orz")
            return 3, base_sdt, df0

    #⑥ピボット判定
    #　判定期間をセット
        cwh_dtx = cwh_dt + dt.timedelta(days=14)  # カップ形成日から約2週間

    #　直近価格がピボットポイントを超える
        df2 = df0.query('@cwh_dt < index < @cwh_dtx & High >= @pvt_p')

    # STEP6判定
        if len(df2.index) > 0:
            pvt_dt = df2.index[0]
            print('STEP6／OK!! ピボット日付:{0}'.format(pvt_dt.date()))
            return 6, pvt_dt, df0
        else:
            print("STEP6／NG...orz")
            return 5, cwh_dt, df0

#---------------------------------------#
# CSVを読取りDataframeを返す
#---------------------------------------#
    def CSV_GetDF(self, doc):
        
        # CSVを読取
        df = pd.read_csv(doc, index_col=0, parse_dates=True)
        df = df.dropna(how='all')                       # 欠損値を除外

    # 移動平均を計算
        df['MA10']   = df['Close'].rolling(self.ma_short).mean()  # 10日移動平均
        df['MA50']   = df['Close'].rolling(self.ma_mid).mean()    # 50日移動平均
        df['MA150']  = df['Close'].rolling(self.ma_s_long).mean() # 150日移動平均
        df['MA200']  = df['Close'].rolling(self.ma_long).mean()   # 200日移動平均
        df['DIFF']   = df['MA200'].pct_change(20)                 # 200日移動平均の変化率
        df['MA_VOL'] = df['Volume'].rolling(self.ma_mid).mean()   # 出来高

        df = df.query('@self.start_dt <= index')        # データ範囲を絞り込み

        return df

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

#------------------------------------------------#
# CSVファイル書込み・チャート作成処理
#------------------------------------------------#
    def writeFlles(self, strTicker, strBaseName, res, strLabel):
        
        # 重複出力を回避
        if (strTicker == self.prevTicker) and (strLabel == self.prevLabel) and (res[1].month == self.prevDate.month):
            return
        
        # ローソク足チャートを作成
#       Out_DIR = self.base_dir + str(res[1].date())
#       # ディレクトリが存在しない場合、ディレクトリを作成
#       if not os.path.exists(Out_DIR):
#           os.makedirs(Out_DIR)
#           i = 0
#           for i in range(3):
#               try:
#                   os.makedirs(Out_DIR)
#               except Exception:
#                   print("\r##ERROR##: Retry=%s" % (str(i)), end="\n", flush=True)
#                   # 5秒スリープしてリトライ
#                   time.sleep(5)
#               else:
#                   # 例外が発生しなかった場合に実行するコード
#                   break  # ループを抜ける

        # チャート出力範囲
        df0 = res[2].tail(260)                   # データを末尾から行数で絞り込み
        df0 = df0.sort_index()                   # 日付で昇順ソート

        # 翌日～30日間の値を取得
        idx_dt1 = res[1]
        idx_dt2 = res[1] + datetime.timedelta(days=30)
        df1 = self.df_ref.query('@idx_dt1 < index <= @idx_dt2')  # 参照用Dataframeから株価を取得
        if len(df1.index) > 0:
            p_Close0  = round(df1.iloc[0]['Open'], 2)    # 翌日の寄値
        else:
            return    # 期間のデータがない場合は抜ける
        
        # 30日間の高値
        rows      = df1['High']
        p_Close30 = round(rows.max(), 2)
        
        # 結果判定
        if p_Close0 * 1.1 < p_Close30:
            strJudge = "○"
        elif p_Close0 * 1.05 < p_Close30:
            strJudge = "△"
        elif p_Close0 < p_Close30:
            strJudge = "▲"
        else:
            strJudge = "×"

        # チャート出力
        # info = self.chart.makeChart(Out_DIR, df0, strTicker, strBaseName, str(res[1].date()) + '@' + str(p_Close0) + '=>' + str(p_Close30) + '\n' + strLabel)

        # Ticker情報を取得
        if strTicker == self.prevTicker:
            shortName = self.prevshortName
            sector    = self.prevsector
        else:
            try:
#               ticker_info = yf.Ticker(strTicker).info
#               shortName   = ticker_info['shortName']
#               sector      = ticker_info['sector']
                ticker_txt = self.chart.txt_info.getTickerInfo(strTicker)
                shortName   = ticker_txt[0]
                sector      = ticker_txt[2]
            except Exception:
                shortName   = '-'
                sector      = '-'

        # CSVファイルの書き込み
        outTxt = strTicker + "," + strLabel + ",\"" + shortName + "\",\"" + sector + "\"," + str(res[1].date()) + "," +  str(p_Close0) + "," +  str(p_Close30) + ",\"" + strJudge + "\"\n"
#       print(outTxt)
        self.w.write(outTxt)
        self.w.flush()

        # 重複出力回避のため情報退避
        self.prevTicker    = strTicker
        self.prevshortName = shortName
        self.prevsector    = sector
        self.prevLabel     = strLabel
        self.prevDate      = res[1].date()

        return
