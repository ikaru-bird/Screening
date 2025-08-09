import sys
import yfinance as yf
import pandas as pd

# yfinanceからindustryを取得
def getTickerIndustry(strTicker):
    # 銘柄関連情報を取得(yfinanceから)
    try:
        ticker = yf.Ticker(strTicker)
        ticker_info = ticker.info
    except:
        ticker_info = []
    # industryを取得
    try:
        industry = ticker_info.get('industry')
    except:
        industry = "----"
    return industry

# ファイルに追記する
def addFile(path_tbl, strLine):
    with open(path_tbl, mode='a', encoding='utf-8') as f:
        f.write(strLine)
    return

# ファイルを読み込む
def readTable(path_tbl):
    df_tbl = pd.read_table(path_tbl, sep='~', names=['Ticker','CompanyName','Sector','industry'], encoding='utf-8')
    df_tbl = df_tbl.drop_duplicates(subset='Ticker', keep='last') # 重複排除、重複時は最後の値を残す
    df_tbl = df_tbl.set_index('Ticker') # indexを設定
    return df_tbl

# ファイルを検索する
def searchIndustry(df_tbl, strTicker):
    try:
#       industry = df_tbl.loc[strTicker, ['industry']]
#       industry = df_tbl.at[strTicker, 'industry']
        industry = str(df_tbl.at[strTicker, 'industry']).replace("—", "-").replace(" - ", "-")
        return industry
    except KeyError:
        return "-----"
