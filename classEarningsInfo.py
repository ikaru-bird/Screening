# coding: UTF-8

# Googleドライブのライブラリを指定(for Google Colab)
import sys
sys.path.append('/content/drive/MyDrive/Colab Notebooks/my-modules')

import requests
import json
import datetime as dt
import time

#---------------------------------------#
# 決算情報検索クラス
#---------------------------------------#
class EarningsInfo():

#---------------------------------------#
# コンストラクタ
#---------------------------------------#
    def __init__(self, strTicker):
        # 日本株の場合、APIを呼び出さず、空データをセット
        if strTicker[-2:] == ".T": # 右から2バイトが".T"の場合＝日本株
            self.json_av  = "{}"   # 空の値をセット(Alpha Vantage)
            self.av_len   = 0      # 0をセット(Alpha Vantage)
            self.json_fmp = "{}"   # 空の値をセット(Financial Modeling Prep)
            self.fmp_len  = 0      # 0をセット(Financial Modeling Prep)
            self.last_dt  = dt.datetime.now() - dt.timedelta(seconds=5) # 現在日時-5秒をセット
            return

        #-------------------------#
        # Alpha Vantage API
        #-------------------------#
        apiKey_av = 'JNB02K8WMWJBO6C5'
        url_av = "https://www.alphavantage.co/query?function=EARNINGS&symbol=" + strTicker + "&apikey=" + apiKey_av
        # エラーリトライ3回
        for i in range(3):
            try:
                res = requests.get(url_av)
                res.raise_for_status() # ステータスコードを確認し、エラー時にエラーを発生させる
            except:
                self.json_av = "{}"   # エラー時は空の値をセット
                self.av_len  = 0      # エラー時は：0をセット
                time.sleep(5)         # 5秒待ってリトライ
            else:
                self.json_av = json.loads(res.text) # JSONオブジェクトを取得
                self.av_len  = len(self.json_av)    # 応答メッセージ長
                break
#       print(json.dumps(self.json_av, indent=4))

        #-------------------------#
        # Financial Modeling Prep
        #-------------------------#
        apiKey_fmp = 'F4vnZZ4rdqTOul76lhySnu92xnZj0YMb'
        url_fmp = "https://financialmodelingprep.com/api/v3/earnings-surprises/" + strTicker + "?apikey=" + apiKey_fmp
        for i in range(3):
            try:
                res = requests.get(url_fmp)
                res.raise_for_status() # ステータスコードを確認し、エラー時にエラーを発生させる
            except:
                self.json_fmp = "{}"   # エラー時は空の値をセット
                self.fmp_len  = 0      # エラー時は：0をセット
                time.sleep(5)          # 5秒待ってリトライ
            else:
                self.json_fmp = json.loads(res.text) # JSONオブジェクトを取得
                self.fmp_len  = len(self.json_fmp)   # 応答メッセージ長
                break
#       print(json.dumps(self.json_fmp, indent=4))

        self.last_dt  = dt.datetime.now() # API最終呼び出し日時をセット
        return

#---------------------------------------#
# 年間EPSの検索関数(Alpha Vantage)
#---------------------------------------#
    def getAnnualEPS(self):
        strAnnualEPS  = "----"
        strCurrentEPS = "----"
        if self.av_len == 0:
            strAnnualEPS = "----"
        else:

            # 通期のEPS比較
            try:
                fiscalDateEnding = str(self.json_av['annualEarnings'][0]['fiscalDateEnding'])
                if fiscalDateEnding[-5:] == "12-31":
                    # 4Qの場合
#                   print("4Q")
                    try:
                        flt_AnnualEPS1 = float(self.json_av['annualEarnings'][0]['reportedEPS'])
                    except:
                        pass
                    try:
                        flt_AnnualEPS2 = float(self.json_av['annualEarnings'][1]['reportedEPS'])
                    except:
                        pass
                else:
                    # 4Q以外の場合
                    try:
                        flt_AnnualEPS1 = float(self.json_av['annualEarnings'][1]['reportedEPS'])
                    except:
                        pass
                    try:
                        flt_AnnualEPS2 = float(self.json_av['annualEarnings'][2]['reportedEPS'])
                    except:
                        pass
            except:
                pass
            
            # 前期の通期のEPS
            try:
                strAnnualEPS = str(round(flt_AnnualEPS2, 2))
            except:
                pass

            # 直近の通期EPS
            try:
                strAnnualEPS += " => " + str(round(flt_AnnualEPS1, 2))
                strCurrentEPS = str(round(flt_AnnualEPS1, 2))
            except:
                pass
            
            # 成長判定マーク
            try:
                if flt_AnnualEPS1 / flt_AnnualEPS2 >= 1.25:
                    strAnnualEPS += " ::: O"
                elif (flt_AnnualEPS1 > 0) and (flt_AnnualEPS2 < 0):
                    strAnnualEPS += " ::: O"
            except:
                pass
        
        return strAnnualEPS, strCurrentEPS

#---------------------------------------#
# 四半期EPSの検索関数(Alpha Vantage)
#---------------------------------------#
    def getQuarterlyEPS(self):
        strQuarterlyEPS = "----"
        
        if self.av_len == 0:
            strQuarterlyEPS = "----"
        else:
            # 直近の四半期EPS
            try:
                strQuarterlyEPS = str(round(float(self.json_av['quarterlyEarnings'][4]['reportedEPS']), 2))
            except:
                pass

            # 前年同期の四半期EPS
            try:
                strQuarterlyEPS += " => " + str(round(float(self.json_av['quarterlyEarnings'][0]['reportedEPS']), 2))
            except:
                pass
            
            # 成長判定マーク
            try:
                if float(self.json_av['quarterlyEarnings'][0]['reportedEPS']) / float(self.json_av['quarterlyEarnings'][4]['reportedEPS']) >= 1.25:
                    strQuarterlyEPS += " ::: O"
                elif (float(self.json_av['quarterlyEarnings'][0]['reportedEPS']) > 0) and (float(self.json_av['quarterlyEarnings'][4]['reportedEPS']) < 0):
                    strQuarterlyEPS += " ::: O"
            except:
                pass
        
        return strQuarterlyEPS

#---------------------------------------------------#
# 直近4Qの決算情報検索関数(Financial Modeling Prep)
#---------------------------------------------------#
    def getQuarterlyEarnings(self):
        strQuarterlyEarnings = ""

        if self.fmp_len == 0:
            strQuarterlyEarnings = "----"
        else:
            for n in range(3):
                if not strQuarterlyEarnings == "":
                    strQuarterlyEarnings += "\n"
                try:
                    # 決算EPS追加
                    try:
                        strQuarterlyEarnings += "'" + self.json_fmp[n]['date'][2:10].replace("-","/") + " "  # 日付の一部のみ取得
                    except:
                        strQuarterlyEarnings += "'--/--/-- "
                    
                    try:
                        strQuarterlyEarnings += str(round(float(self.json_fmp[n]['actualEarningResult']), 2)) + " vs "
                    except:
                        strQuarterlyEarnings += "n/a vs "
                    try:
                        strQuarterlyEarnings += str(round(float(self.json_fmp[n]['estimatedEarning']), 2))
                    except:
                        strQuarterlyEarnings += "n/a"
                    
                    # 決算結果の判定
                    try:
                        surprise = float(self.json_fmp[n]['actualEarningResult']) - float(self.json_fmp[n]['estimatedEarning'])
                    except:
                        result = ""
                    else:
                        if surprise >= 0:
                            result = " :O"
                        else:
                            result = " :X"
                    strQuarterlyEarnings += result
                except:
                    break
        return strQuarterlyEarnings
