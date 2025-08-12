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
        try:
            self.rs_df1 = pd.read_csv(filepath_or_buffer=csvpath1, index_col='Rank') # 業種別
        except (FileNotFoundError, pd.errors.EmptyDataError):
            self.rs_df1 = pd.DataFrame() # 空のDataFrameを作成
        try:
            self.rs_df2 = pd.read_csv(filepath_or_buffer=csvpath2, index_col='Rank') # Ticker別
        except (FileNotFoundError, pd.errors.EmptyDataError):
            self.rs_df2 = pd.DataFrame() # 空のDataFrameを作成

#---------------------------------------#
# IndustryのRelativeStrengthの検索関数
#---------------------------------------#
    def getIndRS(self, str_industry):

        if self.rs_df1.empty:
            return ["----", "----", "----", []]

        # QueryでDataframeを検索
        df = self.rs_df1.query("Industry == @str_industry")

        if len(df) == 0:
            Rank             = "----"
            RelativeStrength = "----"
            Percentile       = "----"
            Tickers          = []
        else:
            Rank             = df.index[0]
            RelativeStrength = round(df.iloc[0]['Relative Strength'],1)
            Percentile       = round(df.iloc[0]['Percentile'])
            Tickers_str      = str(df.iloc[0]['Tickers'])
            Tickers          = Tickers_str.split(",") if Tickers_str != "nan" else []

        return [Rank, RelativeStrength, Percentile, Tickers]

#---------------------------------------#
# TickerのRelativeStrengthの検索関数
#---------------------------------------#
    def getTickerRS(self, str_ticker):

        if self.rs_df2.empty:
            return ["----", "----", "----"]

        # QueryでDataframeを検索
        df = self.rs_df2.query("Ticker == @str_ticker")

        if len(df) == 0:
            Rank             = "----"
            RelativeStrength = "----"
            Percentile       = "----"
        else:
            Rank             = df.index[0]
            RelativeStrength = round(df.iloc[0]['Relative Strength'],1)
            Percentile       = round(df.iloc[0]['Percentile'])

        return [Rank, RelativeStrength, Percentile]
