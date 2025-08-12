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
import matplotlib.font_manager as fm
import japanize_matplotlib
try:
    fp = fm.FontProperties(fname='/content/drive/MyDrive/Colab Notebooks/Fonts/Meiryo/meiryo.ttc')
    plt.rcParams['font.family'] = fp.get_family()
except:
    print("Could not load Meiryo font. Using default.")
    plt.rcParams['font.family'] = "sans-serif"
#---------------------------------------#

#---------------------------------------#
# ローソク足チャート作成クラス
#---------------------------------------#
class DrawChart():

#---------------------------------------#
# コンストラクタ
#---------------------------------------#
    def __init__(self, ma_short, ma_mid, ma_s_long,ma_long, rs_csv1, rs_csv2, info_txt):
        self.ma_short  = ma_short
        self.ma_mid    = ma_mid
        self.ma_s_long = ma_s_long
        self.ma_long   = ma_long
        self.txt_info = TickerInfo(info_txt)
        self.rs = RelativeStrength(rs_csv1, rs_csv2)

    def isfloat(self, s):
        try:
            float(str(s))
        except (ValueError, TypeError):
            return False
        return True

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

    # チャート作成関数
    def makeChart(self, Out_DIR, df, strTicker, strBaseName, strLabel, strUDval, alist, ern_info=None):

        info = ["-","-","-","-","-","-"]
        data = []

        fig = plt.figure(figsize=(12, 6.75), dpi=100)
        fig.subplots_adjust(top=0.93, bottom=0.05, left=0.02, right=0.92, wspace=0.02, hspace=0.0)
        gs = gridspec.GridSpec(ncols=2, nrows=3, width_ratios=[1, 2], height_ratios=[4, 2, 1])

        ax1 = fig.add_subplot(gs[:,0])
        ax2 = fig.add_subplot(gs[0,1])
        ax3 = fig.add_subplot(gs[1,1], sharex=ax2)
        ax4 = fig.add_subplot(gs[2,1], sharex=ax2, ylabel="MACD")

        ax1.axis("tight")
        ax1.axis("off")
        ax2.grid(True, color= 'k', linestyle= '--')
        ax3.grid(True, color= 'k', linestyle= '--')
        ax4.grid(True, color= 'k', linestyle= '--')
        ax3.yaxis.tick_right()
        ax3.yaxis.set_label_position("right")
        ax4.yaxis.tick_right()
        ax4.yaxis.set_label_position("right")

        plt.setp(ax2.get_xticklabels(), visible=False)
        plt.setp(ax3.get_xticklabels(), visible=False)

        macd = self.calc_macd(df, 12, 26, 9)
        apd = [
            mpf.make_addplot(macd['macd'], color='orange', width=0.7, ax=ax4),
            mpf.make_addplot(macd['signal'], color='lime',   width=0.7, ax=ax4),
            mpf.make_addplot(macd['diff+'], type='bar', color='red',   ax=ax4),
            mpf.make_addplot(macd['diff-'], type='bar', color='blue',  ax=ax4),
            mpf.make_addplot(df['Signal'], type='scatter', markersize=50, marker='^', color='#049DBF', ax=ax2)
        ]

        ticker_txt = self.txt_info.getTickerInfo(strTicker)
        strNextErnDt = ticker_txt[5]
        
        ticker_obj = yf.Ticker(strTicker)
        try:
            ticker_info = ticker_obj.info
        except:
            ticker_info = {}

        shortName = ticker_info.get('shortName', "N/A")
        sector = ticker_info.get('sector', "N/A")
        industry = ticker_info.get('industry', "N/A")
        roe = ticker_info.get('returnOnEquity')
        strROE = f"{roe:.1%}" if self.isfloat(roe) else "N/A"

        rs_info1 = self.rs.getTickerRS(strTicker)
        str_tPercentile = str(rs_info1[2])
        rs_info2 = self.rs.getIndRS(industry)
        str_iPercentile = str(rs_info2[2])
        try:
            list_Tickers = rs_info2[3]
            idxTickers = list_Tickers.index(strTicker)
            str_idxTickers = str(idxTickers + 1)
        except:
            str_idxTickers = "----"

        ern = ern_info if ern_info is not None else EarningsInfo(ticker_obj)

        # --- Fundamental Screening ---
        _, fundamental_results = ern.get_fundamental_screening_results(roe)
        fundamental_text_lines = []
        for check_name, (res, reason) in fundamental_results.items():
            status = "O" if res else "X"
            fundamental_text_lines.append(f"{status} : {check_name} : {reason}")
        fundamental_text = "\n".join(fundamental_text_lines)
        # -----------------------------

        strErngs = ern.get_formatted_earnings_summary()

        str52H = "----"
        today  = dt.datetime.now()
        dt52w  = today - dt.timedelta(weeks=52)
        try:
            w52H = round(df['High'][dt52w:today].max(),2)
            p_Close = df.iloc[-1]['Close']
            str52H = f"{w52H} (vs {((p_Close / w52H) - 1):.1%})"
            if p_Close >= w52H:
                str52H +=  " (New High!)"
        except:
            str52H = "----"

        strVolMA = ""
        if (df.iloc[-1]['Volume'] >= df.iloc[-1]['MA_VOL']) and (df.iloc[-1]['Close'] > df.iloc[-1]['Open']):
            strVolMA = "* Vol::OK *"

        strTitle  = f"{strTicker} :: {shortName} {strVolMA}"
        plt.suptitle(strTitle)

        data.append(["Type/Step", strLabel])
        data.append(["Sector\nIndustry", sector + "\n" + industry])
        data.append(["Funds", fundamental_text])
        data.append(["Earnings", strErngs])
        data.append(["NextEarnings", strNextErnDt])
        data.append(["RS Rating",  str_tPercentile + " (ind:" + str_iPercentile + " / rank:" + str_idxTickers + "th)"])
        data.append(["UDVR", strUDval])
        
        ax1_tbl = ax1.table(cellText=data, cellLoc='left', bbox=[0, 0, 1, 1])
        ax1_tbl.auto_set_font_size(False)
        ax1_tbl.set_fontsize(9)

        num_rows = len(data)
        for pos, cell in ax1_tbl.get_celld().items():
            if pos[0] == 2:                      # Funds
                cell.set_height(1.5/num_rows)    # 1.5倍の高さを設定
            elif pos[0] == 3:                    # Earnings
                cell.set_height(3.5/num_rows)    # 3.5倍の高さを設定
            else:
                cell.set_height(1/num_rows)
            
            if pos[1] == 0:
                cell.set_width(0.25) # Adjusted column width
            else:
                cell.set_width(0.75) # Adjusted column width

        try:
            mpf.plot(df, ax=ax2, type='candle', style='yahoo', datetime_format='%Y/%m/%d',
                mav=(self.ma_short, self.ma_mid, self.ma_s_long, self.ma_long),
                volume=ax3, addplot=apd,
                alines={'alines':alist, 'linestyle':'dotted', 'linewidths':1, 'colors':'#cccccc'},
                xlim=(df.index[0], df.index[-1] + dt.timedelta(days=3)),
                tight_layout=True
            )
        except Exception as e:
            print(f'Chart plotting error for {strTicker}: {e}')

        plt.savefig(Out_DIR + '/' + strBaseName + '.png')
        plt.close(fig)

        info[0] = strTicker
        info[1] = shortName
        info[2] = industry
        info[3] = strVolMA
        info[4] = str_iPercentile

        return info
