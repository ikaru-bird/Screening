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
# パーセンタイル計算関数
# --------------------------------------------- #
def calculate_percentile(calp_df, column_name1, column_name2):
    # column_name1に含まれる値が数値でない場合には、0に置き換える
    calp_df[column_name1] = pd.to_numeric(calp_df[column_name1], errors='coerce').fillna(0)
    # パーセンタイルの計算
    total_rows = len(calp_df)
    if total_rows > 1:
        calp_df[column_name2] = (calp_df[column_name1].rank(ascending=True, method='average') - 1) / (total_rows - 1) * 100
    else:
        calp_df[column_name2] = 100 # If only one row, it's 100th percentile
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
    # 結果を格納するDataFrame
    rs_result = pd.DataFrame(columns=["Industry","Ticker","Relative Strength","Diff","RS_1W","RS_1M","RS_3M","RS_6M","RS Momentum","RM_1W","RM_1M","RM_3M","RM_6M"])

    # --- START: Bulk data download ---
    all_tickers = stock_codes['Ticker'].unique().tolist()
    print(f"Found {len(all_tickers)} unique tickers. Downloading all price data in a single batch...")

    start_date = (datetime.now() - timedelta(days=2*365)).strftime("%Y-%m-%d")
    end_date   = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

    # yfinanceから株価データを一括取得
    all_history = yf.download(
        tickers=all_tickers,
        start=start_date,
        end=end_date,
        interval="1d",
        auto_adjust=False,
        prepost=False,
        threads=True,
        progress=False
    )

    if all_history.empty:
        print("Could not download any price data from yfinance. Exiting.")
        return

    # Close price dataframeをffillで補完
    if isinstance(all_history.columns, pd.MultiIndex):
        all_history['Close'] = all_history['Close'].ffill()
    else: # single ticker case
        all_history['Close'] = all_history['Close'].ffill()


    print("Price data download complete. Starting RS calculation...")
    # --- END: Bulk data download ---

    # タイムゾーンと日付の準備 (タイムゾーン情報を削除)
    now = datetime.now()
    W1_ago = now - timedelta(days=7)
    M1_ago = now - timedelta(days=30)
    M3_ago = now - timedelta(days=90)
    M6_ago = now - timedelta(days=180)

    # stock_codesからtickerとindustryをループ処理
    for index, row in stock_codes.iterrows():
        code = row['Ticker']
        sector = row['Industry']

        try:
            # 銘柄の株価データを抽出
            if isinstance(all_history.columns, pd.MultiIndex):
                # If a ticker was not found, it will be missing from the columns
                if code not in all_history.columns.get_level_values(1):
                    continue
                history = all_history.xs(code, level=1, axis=1)
            else:
                # Handle the case where only one ticker was passed to yf.download
                # and it was successful.
                if len(all_tickers) == 1 and all_tickers[0] == code:
                    history = all_history
                else: # Should not happen if MultiIndex check is correct, but as a safeguard.
                    continue

            if history.empty or 'Close' not in history.columns or history['Close'].isnull().all():
                continue

            # 直近1週間のデータがない場合はスキップ
            if len(history.loc[history.index >= W1_ago]) == 0:
                continue

            # 各期間のデータ取得
            history_1w = history.loc[history.index <= W1_ago]
            history_1m = history.loc[history.index <= M1_ago]
            history_3m = history.loc[history.index <= M3_ago]
            history_6m = history.loc[history.index <= M6_ago]

            # RSとRS Momentumの計算
            relative_strength_0 = calculate_relative_strength(history) if not history.empty else 0
            rs_momentum_0 = calculate_rs_momentum(history) if not history.empty else 0

            if relative_strength_0 >= 2000:
                print(f"# Skip  (Code={code}): relative_strength_0 is {relative_strength_0}")
                continue

            relative_strength_w = calculate_relative_strength(history_1w) if not history_1w.empty else 0
            rs_momentum_w = calculate_rs_momentum(history_1w) if not history_1w.empty else 0
            relative_strength_1 = calculate_relative_strength(history_1m) if not history_1m.empty else 0
            rs_momentum_1 = calculate_rs_momentum(history_1m) if not history_1m.empty else 0
            relative_strength_3 = calculate_relative_strength(history_3m) if not history_3m.empty else 0
            rs_momentum_3 = calculate_rs_momentum(history_3m) if not history_3m.empty else 0
            relative_strength_6 = calculate_relative_strength(history_6m) if not history_6m.empty else 0
            rs_momentum_6 = calculate_rs_momentum(history_6m) if not history_6m.empty else 0

            # 結果をDataFrameに追加
            new_row = pd.DataFrame([{
                "Industry": sector,
                "Ticker": code,
                "Relative Strength": relative_strength_0,
                "RS_1W": relative_strength_w,
                "RS_1M": relative_strength_1,
                "RS_3M": relative_strength_3,
                "RS_6M": relative_strength_6,
                "RS Momentum": rs_momentum_0,
                "RM_1W": rs_momentum_w,
                "RM_1M": rs_momentum_1,
                "RM_3M": rs_momentum_3,
                "RM_6M": rs_momentum_6
            }])

            rs_result = pd.concat([rs_result, new_row], ignore_index=True)

        except KeyError:
            continue
        except Exception as e:
            print(f"# Error (Code={code}): {str(e)}")
            continue

    if rs_result.empty:
        print("No tickers were processed successfully. Exiting.")
        return

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
    for sector_name in rs_sector2['Industry']:
        tickers_str = ','.join(rs_result2[rs_result2['Industry'] == sector_name]['Ticker'].tolist())
        rs_sector2.loc[rs_sector2['Industry'] == sector_name, 'Tickers'] = tickers_str

    # indexの変更
    rs_sector2 = rs_sector2.set_index('Rank', drop=True)

    # 不要列の削除
    rs_result2.drop(['RS_1W','RS_1M','RS_3M','RS_6M'], axis=1, inplace=True)
    rs_sector2.drop(['RS_1W','RS_1M','RS_3M','RS_6M'], axis=1, inplace=True)

    # 結果をCSVファイルに保存
    rs_result2.to_csv(rs_result_csv)
    rs_sector2.to_csv(rs_sector_csv)

    return
