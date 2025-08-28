# --------------------------------------------- #
# Relative Strength計算ライブラリ
# --------------------------------------------- #
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import pytz
import time
import random

# --------------------------------------------- #
# Relative Strengthの計算
# --------------------------------------------- #
# Relative Strengthを計算
def calculate_relative_strength(history):
    # Relative Strengthを計算
    try:
        c    = history["Close"].iloc[-1]
    except:
        c    = history["Close"].iloc[0]
    
    try:
        c63  = history["Close"].iloc[-63]
    except:
        c63  = history["Close"].iloc[0]
    
    try:
        c126 = history["Close"].iloc[-126]
    except:
        c126 = history["Close"].iloc[0]
    
    try:
        c189 = history["Close"].iloc[-189]
    except:
        c189 = history["Close"].iloc[0]
    
    try:
        c252 = history["Close"].iloc[-252]
    except:
        c252 = history["Close"].iloc[0]
    
    relative_strength = ((((c - c63) / c63) * 0.4) + (((c - c126) / c126) * 0.2) + (((c - c189) / c189) * 0.2) + (((c - c252) / c252) * 0.2)) * 100
    return round(relative_strength, 2)


# --------------------------------------------- #
# 株価データの取得
# --------------------------------------------- #
# yfinanceから株価データを取得
def getHistoryData(code, start, end):
    # 株価データを取得
    stock = yf.Ticker(code)
#   history = stock.history(period="2y", interval="1d")
    # yfinance >= 0.2.21の変更対応
    history = stock.history(start=start, end=end, interval="1d")
    
    # 終値の列を作成
#   history["Close"] = history["Close"].fillna(method="ffill")  # 非推奨のため↓へ修正
    history["Close"] = history["Close"].ffill()
    return history


# --------------------------------------------- #
# パーセンタイル計算関数
# --------------------------------------------- #
def calculate_percentile(calp_df, column_name1, column_name2):
    # column_name1に含まれる値が数値でない場合には、0に置き換える
    calp_df[column_name1] = pd.to_numeric(calp_df[column_name1], errors='coerce').fillna(0)
    # パーセンタイルの計算
    total_rows = len(calp_df)
    calp_df[column_name2] = (calp_df[column_name1].rank(ascending=True, method='average') - 1) / (total_rows - 1) * 100
    calp_df[column_name2] = calp_df[column_name2].round().clip(1, 99).astype(int)
    return


# --------------------------------------------- #
# RS Momentum計算関数
# --------------------------------------------- #
def calculate_rs_momentum(data):
    # 計算期間（デフォルト14）
    n = 14
    # 終値を使用して計算
    close = data['Close']
    # 価格の変化を計算
    delta = close.diff()
    # 上昇分と下降分に分ける
    gain =  delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    # n日間の平均上昇分と平均下降分
    avg_gain = gain.rolling(window=n, min_periods=1).mean()
    avg_loss = loss.rolling(window=n, min_periods=1).mean()
    # RSの計算
    rs = avg_gain / avg_loss
    # RS Momentumの計算
    rs_momentum = round(rs / (1 + rs),2)
    return rs_momentum.iloc[-1]


# --------------------------------------------- #
# RS計算処理関数
# --------------------------------------------- #
def calc_rs(stock_codes, rs_result_csv, rs_sector_csv):

# --------------------------------------------- #
# 個別RSの計算
# --------------------------------------------- #
    # 業種区分ごとにRelative Strengthを計算し、結果をDataFrameに保存
    rs_result = pd.DataFrame(columns=["Industry","Ticker","Relative Strength","Diff","RS_1W","RS_1M","RS_3M","RS_6M","RS Momentum","RM_1W","RM_1M","RM_3M","RM_6M"])

    
    start = (datetime.now() - timedelta(days=2*365)).strftime("%Y-%m-%d")
    end   = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    
    for sector in stock_codes["Industry"].unique():
        sector_codes = stock_codes[stock_codes["Industry"] == sector]["Ticker"].values.tolist()
        for code in sector_codes:
            try:
                # 過度なアクセスを防ぐために時間（ランダム0.2～1秒）空ける
                time.sleep(random.randrange(200,1000,31)/1000)
                
                history = getHistoryData(code, start, end)
                
                JST = pytz.timezone('Asia/Tokyo')
                W1_ago = datetime.now(JST) - timedelta(days=7)   # 1週間前の日付
                M1_ago = datetime.now(JST) - timedelta(days=30)  # 1ヶ月前の日付
                M3_ago = datetime.now(JST) - timedelta(days=90)  # 3ヶ月前の日付
                M6_ago = datetime.now(JST) - timedelta(days=180) # 6ヶ月前の日付
                
                if len(history.loc[history.index >= W1_ago]) == 0:  # 直近1週間のデータがない場合はスキップ
                    print("# Skip  (Code={}): No price data in last week".format(code))
                    continue
                
                # 各期間のデータ取得
                history_1w = history.loc[history.index <= W1_ago]
                history_1m = history.loc[history.index <= M1_ago]
                history_3m = history.loc[history.index <= M3_ago]
                history_6m = history.loc[history.index <= M6_ago]
                
                try:
                    relative_strength_0 = calculate_relative_strength(history)
                except:
                    relative_strength_0 = 0
                
                if relative_strength_0 >= 2000:  # relative_strength_0が2000以上の場合はスキップ
                    print("# Skip  (Code={}): relative_strength_0 is {}".format(code, relative_strength_0))
                    continue
                    
                try:
                    rs_momentum_0 = calculate_rs_momentum(history)
                except:
                    rs_momentum_0 = 0
                
                try:
                    relative_strength_w = calculate_relative_strength(history_1w)
                except:
                    relative_strength_w = 0
                
                try:
                    rs_momentum_w = calculate_rs_momentum(history_1w)
                except:
                    rs_momentum_w = 0
                
                try:
                    relative_strength_1 = calculate_relative_strength(history_1m)
                except:
                    relative_strength_1 = 0
                
                try:
                    rs_momentum_1 = calculate_rs_momentum(history_1m)
                except:
                    rs_momentum_1 = 0
                
                try:
                    relative_strength_3 = calculate_relative_strength(history_3m)
                except:
                    relative_strength_3 = 0
                
                try:
                    rs_momentum_3 = calculate_rs_momentum(history_3m)
                except:
                    rs_momentum_3 = 0
                
                try:
                    relative_strength_6 = calculate_relative_strength(history_6m)
                except:
                    relative_strength_6 = 0
                
                try:
                    rs_momentum_6 = calculate_rs_momentum(history_6m)
                except:
                    rs_momentum_6 = 0
                
                rs_result_w = pd.DataFrame({
                    "Industry": [sector],
                    "Ticker": [code],
                    "Relative Strength": [relative_strength_0],
                    "RS_1W": [relative_strength_w],
                    "RS_1M": [relative_strength_1],
                    "RS_3M": [relative_strength_3],
                    "RS_6M": [relative_strength_6],
                    "RS Momentum": [rs_momentum_0],
                    "RM_1W": [rs_momentum_w],
                    "RM_1M": [rs_momentum_1],
                    "RM_3M": [rs_momentum_3],
                    "RM_6M": [rs_momentum_6]
                }, index=[0])
                
                rs_result = pd.concat([rs_result.dropna(axis=1, how='all'), rs_result_w.dropna(axis=1, how='all')], ignore_index=True, axis=0)
                
            except Exception as e:
                print("# Error (Code={}): {}".format(code, str(e)))
                continue
    
    # 銘柄のPercentile計算
    calculate_percentile(rs_result, 'Relative Strength', 'Percentile')
    calculate_percentile(rs_result, 'RS_1W', '1 Week Ago')
    calculate_percentile(rs_result, 'RS_1M', '1 Month Ago')
    calculate_percentile(rs_result, 'RS_3M', '3 Months Ago')
    calculate_percentile(rs_result, 'RS_6M', '6 Months Ago')
    
    # 先週とのRS差
    rs_result['Diff'] = rs_result['Relative Strength'] - rs_result['RS_1W']
    
    # Relative Strengthで並び替え
    rs_result2 = rs_result.sort_values('Relative Strength', ascending=False)
    rs_result2 = rs_result2.reset_index(drop=True)
    
    # RANKを作成
    rs_result2['Rank'] = rs_result2.index + 1
    
    # indexの変更
    rs_result2 = rs_result2.set_index('Rank', drop=True)

# --------------------------------------------- #
# 業種別RSの計算
# --------------------------------------------- #
    # Industry列のNaNを文字列（'_UNCLASSIFIED_'）に置換
    rs_result2['Industry'] = rs_result2['Industry'].fillna('_UNCLASSIFIED_')
    # 業種区分ごとの平均値を計算・並び替え・インデックスのリセット
    rs_sector = rs_result2[['Industry','Relative Strength','Diff','RS_1W','RS_1M','RS_3M','RS_6M','RS Momentum','RM_1W','RM_1M','RM_3M','RM_6M']].groupby('Industry').mean()
    rs_sector = rs_sector.sort_values('Relative Strength', ascending=False)
    rs_sector2 = rs_sector.reset_index(drop=False)
    
    # 業種区分RANKを作成
    rs_sector2['Rank'] = rs_sector2.index + 1
    
    # 業種区分のPercentile計算
    calculate_percentile(rs_sector2, 'Relative Strength', 'Percentile')
    calculate_percentile(rs_sector2, 'RS_1W', '1 Week Ago')
    calculate_percentile(rs_sector2, 'RS_1M', '1 Month Ago')
    calculate_percentile(rs_sector2, 'RS_3M', '3 Months Ago')
    calculate_percentile(rs_sector2, 'RS_6M', '6 Months Ago')
    
    # 先週とのRS差
    rs_sector2['Diff'] = rs_sector2['Relative Strength'] - rs_sector2['RS_1W']
    
    # 該当するコードを連結
    rs_sector2['Tickers'] = ""
    for sector in rs_sector2['Industry']:
        tickers_str = ','.join(rs_result2[rs_result2['Industry'] == sector]['Ticker'].tolist())
        rs_sector2.loc[rs_sector2['Industry'] == sector, 'Tickers'] = tickers_str
    
    # indexの変更
    rs_sector2 = rs_sector2.set_index('Rank', drop=True)
    
    # 不要列の削除
    rs_result2.drop(['RS_1W','RS_1M','RS_3M','RS_6M'], axis=1, inplace=True)
    rs_sector2.drop(['RS_1W','RS_1M','RS_3M','RS_6M'], axis=1, inplace=True)
    
    # 結果をCSVファイルに保存
    rs_result2.to_csv(rs_result_csv)
    rs_sector2.to_csv(rs_sector_csv)
    
    return
