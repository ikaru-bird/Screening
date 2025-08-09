# coding: UTF-8

import sys
sys.path.append('/content/drive/My Drive/Colab Notebooks/my-modules')

import pandas as pd
import numpy as np

#---------------------------------------#
# 相対強度(RS)の検索クラス
#---------------------------------------#
class RelativeStrength():

#---------------------------------------#
# コンストラクタ
#---------------------------------------#
    def __init__(self, csvpath1, csvpath2):

        # 業種別RS CSVの読み込み
        try:
            self.rs_df1 = pd.read_csv(filepath_or_buffer=csvpath1) # 業種別
        except (FileNotFoundError, pd.errors.EmptyDataError):
            # ファイルが存在しない、または空の場合は空のDataFrameを作成
            self.rs_df1 = pd.DataFrame(columns=['Industry', 'RS', 'Rank', 'Percentile', 'Tickers'])

        # 銘柄別RS CSVの読み込み
        try:
            self.rs_df2 = pd.read_csv(filepath_or_buffer=csvpath2) # 銘柄別
        except (FileNotFoundError, pd.errors.EmptyDataError):
            # ファイルが存在しない、または空の場合は空のDataFrameを作成
            self.rs_df2 = pd.DataFrame(columns=['Ticker', 'RS', 'Rank', 'Percentile'])

#---------------------------------------#
# 業種別RSの検索関数
#---------------------------------------#
    def getIndRS(self, ind):
        try:
            # 業種名で検索
            target = self.rs_df1[self.rs_df1['Industry'] == ind]

            # 検索結果の件数
            if len(target) > 0:
                # 戻り値をセット
                rank = target.iloc[0,2]
                val  = target.iloc[0,3]
                per  = target.iloc[0,4]
                tcks = target.iloc[0,5].split(',')
            else:
                # 該当なしの場合は固定値をセット
                rank = 999
                val  = 0
                per  = 0
                tcks = []
        except:
            # 例外発生時は固定値をセット
            rank = 999
            val  = 0
            per  = 0
            tcks = []

        return rank, val, per, tcks

#---------------------------------------#
# 銘柄別RSの検索関数
#---------------------------------------#
    def getTickerRS(self, tck):
        try:
            # Tickerで検索
            target = self.rs_df2[self.rs_df2['Ticker'] == tck]

            # 検索結果の件数
            if len(target) > 0:
                # 戻り値をセット
                rank = target.iloc[0,2]
                val  = target.iloc[0,3]
                per  = target.iloc[0,4]
            else:
                # 該当なしの場合は固定値をセット
                rank = 999
                val  = 0
                per  = 0
        except:
            # 例外発生時は固定値をセット
            rank = 999
            val  = 0
            per  = 0

        return rank, val, per
