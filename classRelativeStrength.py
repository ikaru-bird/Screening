# coding: UTF-8

# Googleドライブのライブラリを指定(for Google Colab)
import sys
sys.path.append('/content/drive/MyDrive/Colab Notebooks/my-modules')

import pandas as pd

#---------------------------------------#
# Relative Strength検索クラス
#---------------------------------------#
class RelativeStrength():

#---------------------------------------#
# コンストラクタ
#---------------------------------------#
    def __init__(self, csvpath1, csvpath2):
        # CSVファイルの読み込み
        self.rs_df1 = pd.read_csv(filepath_or_buffer=csvpath1) # 業種別
        self.rs_df2 = pd.read_csv(filepath_or_buffer=csvpath2) # Ticker別

#---------------------------------------#
# IndustryのRelativeStrengthの検索関数
#---------------------------------------#
    def getIndRS(self, str_industry):
        
        # QueryでDataframeを検索
        df = self.rs_df1.query("Industry == @str_industry")
        
        if len(df) == 0:
            Rank             = "----"
            RelativeStrength = "----"
            Percentile       = "----"
            Tickers          = "----"
        else:
            Rank             = df.iloc[0]['Rank']
            RelativeStrength = round(df.iloc[0]['Relative Strength'],1)
            Percentile       = round(df.iloc[0]['Percentile'])
            Tickers          = str(df.iloc[0]['Tickers']).split(",")
        
        return [Rank, RelativeStrength, Percentile, Tickers]

#---------------------------------------#
# TickerのRelativeStrengthの検索関数
#---------------------------------------#
    def getTickerRS(self, str_ticker):
        
        # QueryでDataframeを検索
        df = self.rs_df2.query("Ticker == @str_ticker")
        
        if len(df) == 0:
            Rank             = "----"
            RelativeStrength = "----"
            Percentile       = "----"
        else:
            Rank             = df.iloc[0]['Rank']
            RelativeStrength = round(df.iloc[0]['Relative Strength'],1)
            Percentile       = round(df.iloc[0]['Percentile'])
        
        return [Rank, RelativeStrength, Percentile]

