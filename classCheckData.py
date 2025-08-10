# coding: UTF-8

import sys
sys.path.append('/content/drive/MyDrive/Colab Notebooks/my-modules')

import os, fnmatch
import pandas as pd
import datetime as dt
import time
from classDrawChart import DrawChart

class CheckData():
    def __init__(self, out_path, chart_dir, ma_short, ma_mid, ma_s_long, ma_long, rs_csv1, rs_csv2, txt_path):
        self.ma_short   = ma_short
        self.ma_mid     = ma_mid
        self.ma_s_long  = ma_s_long
        self.ma_long    = ma_long
        self.outPeriod = 7
        self.df = pd.DataFrame()
        self.strBaseName = "---"
        self.strTicker   = "---"
        self.today = dt.datetime.now()
        self.base_dir = chart_dir
        self.chart = DrawChart(self.ma_short, self.ma_mid, self.ma_s_long, self.ma_long, rs_csv1, rs_csv2, txt_path)
        self.ern_info = None
        is_file = os.path.isfile(out_path)
        if is_file:
            self.w = open(out_path, mode="a", encoding="utf-8", errors="ignore")
        else:
            self.w = open(out_path, mode="w", encoding="utf-8", errors="ignore")
            self.w.write("\"日付\",\"タイプ\",\"コード\",\"会社名\",\"業種区分\",\"業種RS\",\"UDVR\",\"UDVR.prev\",\"UD判定\",\"VOLUME\",\"fwdPER\",\"Price\"\n")
            self.w.flush()

    def __del__(self):
        if hasattr(self, 'w'):
            self.w.close()

    def set_earnings_info(self, ern_info):
        self.ern_info = ern_info

    def isTrendTemplete(self):
        res = self.TrendTemplete_Check()
        if res is None: return
        if res[0] >= 7:
            print(self.strTicker + " is ::: Trend Templete ::: ")
            self.isBuySign()

    def isBuySign(self):
        res_cwh = self.Cup_with_Handle_Check()
        if res_cwh and res_cwh[0] >= 4 and abs(self.today - res_cwh[1]).days <= self.outPeriod:
            self.writeFlles(res_cwh, f"cup with handle({res_cwh[0]})")
        # ... (other patterns)

    def isON_Minervini(self):
        res = self.ON_Minervini_Check()
        if res and res[0] == 1 and abs(self.today - res[1]).days <= self.outPeriod:
            self.writeFlles(res, "Base Formation")

    # ... (All other is... methods like isGranville, isGoldernCross etc.)
    def isGranville(self):
        res = self.BuyPoint_Check()
        if res and abs(self.today - res[1]).days <= self.outPeriod and res[0] in [1, 3, 50]:
            self.writeFlles(res, f"buy sign({res[0]})")

    def isGoldernCross(self):
        res = self.GC_Check()
        if res and abs(self.today - res[1]).days <= self.outPeriod and res[0] != "0":
            self.writeFlles(res, f"golden cross({res[0]})")

    def TrendTemplete_Check(self):
        df0 = self.df
        if not isinstance(df0.index, pd.DatetimeIndex):
            return None
        if len(df0.index) < 200:
            return None
        # ... (rest of the logic)
        idxtoday = df0.index[-1]
        close_p  = df0.loc[idxtoday, 'Close']
        if any(pd.isna(df0.loc[idxtoday, ma]) for ma in ['MA50', 'MA150', 'MA200']): return None
        if not (close_p >= df0.loc[idxtoday, 'MA150'] and close_p >= df0.loc[idxtoday, 'MA200']): return 0, idxtoday
        if not (df0.loc[idxtoday, 'MA150'] >= df0.loc[idxtoday, 'MA200']): return 1, idxtoday
        # ... etc
        return 7, idxtoday

    def ON_Minervini_Check(self):
        # ... (The full original code for this method)
        return 0, None, [] # dummy return

    def csvSetDF(self, doc):
        df = pd.read_csv(doc, index_col=0, on_bad_lines='skip')
        df.index = pd.to_datetime(df.index, errors='coerce')
        df.dropna(inplace=True, subset=[df.index.name])
        df = df.astype(float, errors='ignore')
        df['MA10']   = df['Close'].rolling(self.ma_short).mean()
        df['MA50']   = df['Close'].rolling(self.ma_mid).mean()
        df['MA150']  = df['Close'].rolling(self.ma_s_long).mean()
        df['MA200']  = df['Close'].rolling(self.ma_long).mean()
        df['DIFF']   = df['MA200'].pct_change(20)
        df['MA_VOL'] = df['Volume'].rolling(self.ma_mid).mean()
        self.df = df
        self.strBaseName = os.path.splitext(os.path.basename(doc))[0]
        self.strTicker = self.strBaseName.replace('-X', '')
        return

    def writeFlles(self, res, strLabel):
        print(self.strTicker + " is ::: " + strLabel + " :::")
        # ... (rest of the method)
        info = self.chart.makeChart(self.base_dir, self.df, self.strTicker, self.strBaseName, strLabel, "ud_val_placeholder", res[2] if len(res) > 2 else [], ern_info=self.ern_info)
        # ... (rest of the method)

    # All other original check methods (Cup_with_Handle_Check, etc.) must be present here
    def Cup_with_Handle_Check(self): return 0, dt.datetime.now(), []
    def FlatBase_Check(self): return 0, dt.datetime.now(), []
    def DoubleBottom_Check1(self): return 0, dt.datetime.now(), []
    def DoubleBottom_Check2(self): return 0, dt.datetime.now(), []
    def VCP_Check1(self): return 0, dt.datetime.now(), []
    def VCP_Check2(self): return 0, dt.datetime.now(), []
    def BuyPoint_Check(self): return 0, dt.datetime.now(), []
    def GC_Check(self): return "0", dt.datetime.now(), []
    def ShortSign_Check(self): return 0, dt.datetime.now(), []
    def calcUDRatio(self, df0): return 0.0
