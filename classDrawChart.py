# coding: UTF-8

# Googleドライブのライブラリを指定(for Google Colab)
import sys
sys.path.append('/content/drive/MyDrive/Colab Notebooks/my-modules')

import datetime as dt
import time
import pandas as pd
import yfinance as yf
import numpy as np
import mplfinance as mpf
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import gridspec
from classTickerInfo import TickerInfo
from classRelativeStrength import RelativeStrength
from classEarningsInfo import EarningsInfo

#---------------------------------------#
# フォント指定（日本語対応）
#---------------------------------------#
# Google Colab実行の場合
# Googleドライブ上のフォントファイルを指定
import matplotlib.font_manager as fm
import japanize_matplotlib
fp = fm.FontProperties(fname='/content/drive/MyDrive/Colab Notebooks/Fonts/Meiryo/meiryo.ttc')
plt.rcParams['font.family'] = fp.get_family()
#---------------------------------------#
# PC実行の場合
# フォントに'メイリオ'を指定
#plt.rcParams['font.family'] = "Meiryo"
#---------------------------------------#

#---------------------------------------#
# ローソク足チャート作成クラス
#---------------------------------------#
class DrawChart():

#---------------------------------------#
# コンストラクタ
#---------------------------------------#
    def __init__(self, ma_short, ma_mid, ma_s_long,ma_long, rs_csv1, rs_csv2, info_txt):
        # 移動平均の期間をセット
        self.ma_short  = ma_short
        self.ma_mid    = ma_mid
        self.ma_s_long = ma_s_long
        self.ma_long   = ma_long
        
        # Ticker情報検索クラスを作成
        self.txt_info = TickerInfo(info_txt)
        
        # Relative Strengthクラスを作成
        self.rs = RelativeStrength(rs_csv1, rs_csv2)
        
        # Alpha Vantage APIの呼び出し回数制御のため前回呼び出し日時保持
        # 初期値：現在日時 -5秒をセット
        self.ern_last_dt = dt.datetime.now() - dt.timedelta(seconds=5)

    # 浮動小数点数値かどうかを判定する関数
    def isfloat(self, s):
        try:
            float(str(s))  # float関数で文字列を変換
        except ValueError:
            return False  # 失敗すれば False
        else:
            return True   # 上手くいけば True

    # MACD計算関数
    def calc_macd(self, df, es, el, sg):
        macd = pd.DataFrame()
        macd['ema_s'] = df['Close'].ewm(span=es).mean()
        macd['ema_l'] = df['Close'].ewm(span=el).mean()
        macd['macd'] = macd['ema_s'] - macd['ema_l']
        macd['signal'] = macd['macd'].ewm(span=sg).mean()
        macd['diff'] = macd['macd'] - macd['signal']
        f_plus = lambda x: x if x > 0 else 0
        f_minus = lambda x: x if x < 0 else 0
        macd['diff+'] = macd['diff'].map(f_plus)
        macd['diff-'] = macd['diff'].map(f_minus)
        return macd

    # UTCをJSTに変換
    def utc_to_jst(self, timestamp_utc):
        datetime_utc  = dt.datetime.strptime(timestamp_utc + "+0000", "%Y/%m/%d %H:%M%z")
        datetime_jst  = datetime_utc.astimezone(dt.timezone(dt.timedelta(hours=+9)))
        timestamp_jst = dt.datetime.strftime(datetime_jst, "%Y/%m/%d %H:%M")
        return timestamp_jst

    # チャート作成関数
    def makeChart(self, Out_DIR, df, strTicker, strBaseName, strLabel, strUDval, alist):
        
        info = ["-","-","-","-","-","-"]
        data = []
        
        # figureを作成
        fig = plt.figure(figsize=(12, 6.75), dpi=100)
        fig.subplots_adjust(top=0.93, bottom=0.05, left=0.02, right=0.92, wspace=0.02, hspace=0.0)
        
        # subplotのサイズ指定
        gs = gridspec.GridSpec(ncols=2, nrows=3, width_ratios=[1, 2], height_ratios=[4, 2, 1])
        
        # subplotを追加
        ax1 = fig.add_subplot(gs[:,0])
        ax2 = fig.add_subplot(gs[0,1])
        ax3 = fig.add_subplot(gs[1,1], sharex=ax2)
        ax4 = fig.add_subplot(gs[2,1], sharex=ax2, ylabel="MACD")
        
        # 表示設定
        ax1.axis("tight")
        ax1.axis("off")
        ax2.grid(True, color= 'k', linestyle= '--')
        ax3.grid(True, color= 'k', linestyle= '--')
        ax4.grid(True, color= 'k', linestyle= '--')
        ax3.yaxis.tick_right()
        ax3.yaxis.set_label_position("right")
        ax4.yaxis.tick_right()
        ax4.yaxis.set_label_position("right")
        
        # X軸を表示しない
        plt.setp(ax2.get_xticklabels(), visible=False)
        plt.setp(ax3.get_xticklabels(), visible=False)
        
        # MACDの計算・判定マークの表示設定
        macd = self.calc_macd(df, 12, 26, 9)
        rdf1 = macd['macd'].to_numpy()
        rdf2 = macd['signal'].to_numpy()
        rdf3 = macd['diff+'].to_numpy()
        rdf4 = macd['diff-'].to_numpy()
        rdf5 = df['Signal'].to_numpy()   # 判定マーク
        apd = [
            mpf.make_addplot(rdf1, color='orange', width=0.7, ax=ax4),
            mpf.make_addplot(rdf2, color='lime',   width=0.7, ax=ax4),
            mpf.make_addplot(rdf3, type='bar', color='red',   ax=ax4),
            mpf.make_addplot(rdf4, type='bar', color='blue',  ax=ax4),
            mpf.make_addplot(rdf5, type='scatter', markersize=50, marker='^', color='#049DBF', ax=ax2)
        ]
        
        # 銘柄関連情報を取得(テキストファイルから)
        ticker_txt = self.txt_info.getTickerInfo(strTicker)
        
        # 銘柄関連情報を取得(yfinanceから)
        try:
            ticker = yf.Ticker(strTicker)
            ticker_info = ticker.info
        except:
            ticker_info = []
        
        # 会社名の取得
        shortName = ticker_txt[0]
        
        # セクターの取得
        sector = ticker_txt[1]
        
        # 産業分野の取得
        industry = ticker_txt[2]
        
        # PER(trailingPE)を取得
        try:
            trailingPE = ticker_info.get('trailingPE')
        except:
            trailingPE = ticker_txt[3]
        # 出力用に整形
        if self.isfloat(trailingPE) == True:
            strTrailingPE = str(round(float(trailingPE), 1))
        else:
            strTrailingPE = "----"
        
        # 予想PER(forwardPE)を取得
        try:
            forwardPE = ticker_info.get('forwardPE')
        except:
            forwardPE = ticker_txt[4]
        forwardPE = ticker_txt[4]
        # 出力用に整形
        if self.isfloat(forwardPE) == True:
            strForwardPE = str(round(float(forwardPE), 1))
        else:
            strForwardPE = "----"
        
        # Ticker別Relative Strengthの検索
        rs_info1 = self.rs.getTickerRS(strTicker)
        str_tRank             = str(rs_info1[0])   # TickerRSランク
        str_tRelativeStrength = str(rs_info1[1])   # RelativeStrength値
        str_tPercentile       = str(rs_info1[2])   # RelativeStrengthパーセント
        
        # 産業別Relative Strengthの検索
        rs_info2 = self.rs.getIndRS(industry)
        str_iRank             = str(rs_info2[0])   # 業種RSランク
        str_iRelativeStrength = str(rs_info2[1])   # RelativeStrength値
        str_iPercentile       = str(rs_info2[2])   # RelativeStrengthパーセント
        list_Tickers          = rs_info2[3]        # Tickerのリスト
        try:
            idxTickers     = list_Tickers.index(strTicker)
            str_idxTickers = str(idxTickers + 1) # Tickerの業種内ランク
        except:
            str_idxTickers = "----"
        
        # 業種RSが60未満の場合はチャートを作成せず抜ける
        # try:
        #     if self.isfloat(rs_info2[2]) == True:
        #         if rs_info2[2] < 60:
        #             print("Pass :::ind_RS is " + str_iPercentile)
        #             return info
        # except:
        #     pass
        
        # 決算情報検索クラスの前回呼び出し時から5秒空ける
        delta = dt.datetime.now() - self.ern_last_dt
        if delta.total_seconds() < 5:
            time.sleep(5 - delta.total_seconds())
        
        # 決算情報検索クラスを作成
        ern = EarningsInfo(strTicker)
        self.ern_last_dt = ern.last_dt
        
        # 決算
        strErngs = ern.getQuarterlyEarnings()
        
        # EPSを取得
        #  Alpha Vantageから
        strQuarterlyEPS = ern.getQuarterlyEPS()
        AnnualEPS       = ern.getAnnualEPS()
        strAnnualEPS    = AnnualEPS[0]
        epsCurrentYear  = AnnualEPS[1]
        #  yfinanceから
        try:
            epsTrailing12M = round(float(ticker_info.get('trailingEps')), 2)
        except:
            epsTrailing12M = "----"
        
        if strQuarterlyEPS == "----":
            strEPS =  str(epsTrailing12M) + "\n"
        else:
            strEPS =  strQuarterlyEPS + "\n"
        
        if strAnnualEPS == "----":
            strEPS += str(epsCurrentYear) + "\n"
        else:
            strEPS += strAnnualEPS + "\n"
        
        # EPS予想を取得
        try:
            epsForward = ticker_info.get('forwardEps')
        except:
            epsForward = "----"
        # 出力用に整形
        if (self.isfloat(epsForward) == True) and (self.isfloat(epsCurrentYear) == True):
            strEPSfwd = str(round(epsForward, 2))
            try:
                if (float(epsForward) > 0) and (float(epsForward) / float(epsCurrentYear) >= 1.25):
                    strEPSfwd = strEPSfwd + " ::: O"
                elif (float(epsForward) > 0) and (float(epsCurrentYear) < 0):
                    strEPSfwd = strEPSfwd + " ::: O"
            except:
                pass
            
        elif (self.isfloat(epsForward) == True) and (self.isfloat(epsCurrentYear) == False):
            strEPSfwd = str(round(float(epsForward), 2))
        else:
            strEPSfwd = "----"
        strEPS += strEPSfwd
        
        # 52週高値
        str52H = "----"
        today  = dt.datetime.now()
        dt52w  = today - dt.timedelta(weeks=52)
        try:
            w52H = round(df['High'][dt52w:today].max(),2)
        except:
            str52H = "----"
        else:
            str52H = str(w52H)
            p_Close = df.iloc[-1]['High']
            if p_Close >= w52H:
                str52H = str52H +  " ::: *"
            elif p_Close / w52H >= 0.75:
                str52H = str52H +  " ::: O"
        
        # 次回決算日
        strNextErnDt = ticker_txt[5]
        
        #全体のタイトル
        strVolMA = ""
        if (df.iloc[-1]['Volume'] >= df.iloc[-1]['MA_VOL']) and (df.iloc[-1]['Close'] > df.iloc[-1]['Open']):
            strVolMA = "* Vol::OK *"
        
        strTitle  = strTicker + ' :: ' + shortName + ' ' + strVolMA
        plt.suptitle(strTitle)
        
        # テーブルに出力項目を追加
        data.append(["Type/Step", strLabel])
        data.append(["Sector", sector])
        data.append(["Industry", industry])
        data.append(["PER / fwdPER", strTrailingPE + " / " + strForwardPE])
        data.append(["EPS: YoY\nEPS: Anual\nEPS: Fwd", strEPS])
        data.append(["Earnings", strErngs])
        data.append(["Next Earnings", strNextErnDt])
        data.append(["UDVR", strUDval])
        data.append(["RS Rating",  str_tPercentile + " (ind:" + str_iPercentile + " / rank:" + str_idxTickers + "th)"])
        data.append(["52wkHigh", str52H])
        
        # テーブル出力
        ax1_tbl = ax1.table(cellText=data, cellLoc='left', bbox=[0, 0, 1, 1])

        # テーブルのフォントサイズを固定
        ax1_tbl.auto_set_font_size(False)
        ax1_tbl.set_fontsize(10)

        # テーブルの高さ・背景色を調整
        i = 0 # カウンタ
        for pos, cell in ax1_tbl.get_celld().items():
            cell.set_height(1/len(data))
            if i%2 == 0: # 偶数の場合
                cell.set_facecolor('#dcdcdc') # 背景着色
                cell.set_width(0.4)           # セル幅セット
            else:
                cell.set_width(0.6)           # セル幅セット
            
            i += 1 # カウンタ加算

        # チャート出力
        try:
            mpf.plot(df,            # データフレーム
                ax=ax2,             # グラフの出力先
                type='candle',      # グラフ表示の種類
                style='yahoo',      # スタイル指定
                datetime_format='%Y/%m/%d', # 日付の表示形式
                mav=(self.ma_short, self.ma_mid, self.ma_s_long, self.ma_long),  # 移動平均線
                volume=ax3,         # ボリュームの表示
                addplot=apd,        # MACDの表示
                alines={'alines':alist, 'linestyle':'dotted', 'linewidths':1, 'colors':'#cccccc'},  # 補助線の追加
                xlim=(df.index[0], df.index[-1] + dt.timedelta(days=3)), # X軸の表示幅
                tight_layout=True   # 余白を減らす
            )
        except ValueError as e:
            # ValueError発生時は補助線を出力しない
            print('ValueError:', e)
            mpf.plot(df,            # データフレーム
                ax=ax2,             # グラフの出力先
                type='candle',      # グラフ表示の種類
                style='yahoo',      # スタイル指定
                datetime_format='%Y/%m/%d', # 日付の表示形式
                mav=(self.ma_short, self.ma_mid, self.ma_s_long, self.ma_long),  # 移動平均線
                volume=ax3,         # ボリュームの表示
                addplot=apd,        # MACDの表示
                xlim=(df.index[0], df.index[-1] + dt.timedelta(days=3)), # X軸の表示幅
                tight_layout=True   # 余白を減らす
            )
        
        # 画像ファイルを保存
        plt.savefig(Out_DIR + '/' + strBaseName + '.png')
        plt.close()

        # 戻り値をセット
        info[0]   = strTicker
        info[1]   = shortName
        info[2]   = industry
        info[3]   = strVolMA
        info[4]   = str_iPercentile
        info[5]   = strForwardPE

        return info
