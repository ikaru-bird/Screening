# coding: UTF-8

import pandas as pd

#---------------------------------------#
# Ticker情報検索クラス
#---------------------------------------#
class TickerInfo():

#---------------------------------------#
# コンストラクタ
#---------------------------------------#
    def __init__(self, csvpath):
        # CSVファイルの読み込み
        self.ti_df = pd.read_csv(filepath_or_buffer=csvpath, sep='~', header=None, names=['Ticker','Company','Sector','Industry','MarketCap','PE','FwdPE','Earnings','Volume','Price'], index_col="Ticker", encoding='utf-8')
        # self.ti_df.fillna('----', inplace=True)
        self.ti_df = self.ti_df.astype(str)
        self.ti_df.fillna('----', inplace=True)

#       print(self.ti_df)

#---------------------------------------#
# 属性情報の検索関数
#---------------------------------------#
    def getTickerInfo(self, str_Ticker):
        
        # QueryでDataframeを検索
        df = self.ti_df.query("Ticker == @str_Ticker")
        
        if len(df) == 0:
            Company     = "----"
            Sector      = "----"
            Industry    = "----"
            PE          = "----"
            FwdPE       = "----"
            Earnings    = "----"
        else:
            Company     = df.iloc[0]['Company']
            Sector      = df.iloc[0]['Sector']
            Industry    = df.iloc[0]['Industry']
            PE          = df.iloc[0]['PE']
            FwdPE       = df.iloc[0]['FwdPE']
            Earnings    = df.iloc[0]['Earnings']
        
        return [Company, Sector, Industry, PE, FwdPE, Earnings]

