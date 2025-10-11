# --------------------------------------------- #
# Relative Strength計算ライブラリ
# --------------------------------------------- #
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import pytz
import time

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
# RS計算処理関数 (ベクトル化対応)
# --------------------------------------------- #

def _process_ticker_group(group):
    """
    1銘柄分のデータ(group)を受け取り、RS関連指標を計算して返す。
    `groupby().apply()`での使用を想定。
    """
    # groupby()から渡されるgroupのインデックスはMultiIndex('Date', 'Ticker')になっている。
    # 'Ticker'レベルを削除して、インデックスをDatetimeIndexに戻す。
    group = group.reset_index(level='Ticker', drop=True)

    group = group.dropna(how='all')
    if group.empty:
        return None

    # タイムゾーンを日本時間に設定
    JST = pytz.timezone('Asia/Tokyo')

    # タイムゾーン情報がない場合はUTCを付与
    if group.index.tz is None:
        group.index = group.index.tz_localize('UTC')

    # 直近1週間のデータがなければスキップ
    W1_ago = datetime.now(JST) - timedelta(days=7)
    if len(group.loc[group.index >= W1_ago]) == 0:
        return None

    # 終値データを前方補完
    group["Close"] = group["Close"].ffill()
    if group['Close'].isnull().all():
        return None

    # 各期間の日付を定義
    M1_ago = datetime.now(JST) - timedelta(days=30)
    M3_ago = datetime.now(JST) - timedelta(days=90)
    M6_ago = datetime.now(JST) - timedelta(days=180)

    # 各期間の株価データを抽出
    history_1w = group.loc[group.index <= W1_ago]
    history_1m = group.loc[group.index <= M1_ago]
    history_3m = group.loc[group.index <= M3_ago]
    history_6m = group.loc[group.index <= M6_ago]

    # オリジナルの実装に倣い、例外処理を含めて各指標を計算
    try:
        relative_strength_0 = calculate_relative_strength(group)
    except:
        relative_strength_0 = 0

    # 元のコードにあったスキップ条件
    if relative_strength_0 >= 2000:
        return None

    try:
        rs_momentum_0 = calculate_rs_momentum(group)
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

    # 計算結果をPandas Seriesとして返す
    return pd.Series({
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
    })

def calc_rs(stock_codes, rs_result_csv, rs_sector_csv):

    # --------------------------------------------- #
    # 全銘柄の株価データを分割取得 (変更なし)
    # --------------------------------------------- #
    all_tickers = stock_codes["Ticker"].unique().tolist()
    chunk_size = 200
    all_data_list = []

    ticker_chunks = [all_tickers[i:i + chunk_size] for i in range(0, len(all_tickers), chunk_size)]

    print(f"Found {len(all_tickers)} tickers. Downloading data in {len(ticker_chunks)} chunks of up to {chunk_size} tickers each.")

    start_date = (datetime.now() - timedelta(days=2*365)).strftime("%Y-%m-%d")
    end_date   = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

    for i, chunk in enumerate(ticker_chunks):
        print(f"Downloading chunk {i + 1}/{len(ticker_chunks)}...")
        try:
            data = yf.download(
                tickers=chunk,
                start=start_date,
                end=end_date,
                interval="1d",
                auto_adjust=True,
                prepost=False,
                threads=True,
                progress=False
            )
            if not data.empty:
                all_data_list.append(data)
            else:
                print(f"Warning: No data returned for chunk {i + 1}.")

            # 次のチャンクへ進む前に5秒待機 (ユーザー指示により維持)
            if i < len(ticker_chunks) - 1:
                time.sleep(5)

        except Exception as e:
            print(f"Error downloading chunk {i + 1}: {e}")
            continue

    if not all_data_list:
        print("Could not download any price data from yfinance after all chunks.")
        return

    all_data = pd.concat(all_data_list, axis=1)
    print("Price data download complete. Starting analysis...")

    # --------------------------------------------- #
    # 個別RSの計算 (ベクトル化処理)
    # --------------------------------------------- #
    # yfinanceの複数銘柄データ(MultiIndex)を整形
    # (カラム: ('Close', 'AAPL')) -> (インデックス: ('Date', 'Ticker'), カラム: 'Close')
    data_stacked = all_data.stack(level=1, future_stack=True).rename_axis(index=['Date', 'Ticker'])

    # CloseがNaNの行（データ欠損）を削除して、RuntimeWarningを回避
    data_stacked.dropna(subset=['Close'], inplace=True)

    # Ticker毎にグループ化し、RS計算関数を適用
    rs_result = data_stacked.groupby(level='Ticker').apply(_process_ticker_group)

    # 計算結果がNoneだった行(スキップ対象)を削除
    rs_result.dropna(how='all', inplace=True)

    if rs_result.empty:
        print("No data to process after calculations. Exiting.")
        return

    # 銘柄情報(業種)をマージ
    rs_result = rs_result.reset_index()
    rs_result = pd.merge(rs_result, stock_codes[['Ticker', 'Industry']], on='Ticker', how='left')

    # 元のスクリプトと列の順序を合わせる
    cols_in_order = [
        "Industry", "Ticker", "Relative Strength", "RS_1W", "RS_1M", "RS_3M", "RS_6M",
        "RS Momentum", "RM_1W", "RM_1M", "RM_3M", "RM_6M"
    ]
    # 存在しない列を指定するとエラーになるため、存在する列のみで順序を定義
    ordered_cols = [col for col in cols_in_order if col in rs_result.columns]
    rs_result = rs_result[ordered_cols]

    # --------------------------------------------- #
    # Percentile計算以降の処理 (変更なし)
    # --------------------------------------------- #
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
    # 業種別RSの計算 (変更なし)
    # --------------------------------------------- #
    rs_result2['Industry'] = rs_result2['Industry'].fillna('_UNCLASSIFIED_')
    rs_sector = rs_result2[['Industry','Relative Strength','Diff','RS_1W','RS_1M','RS_3M','RS_6M','RS Momentum','RM_1W','RM_1M','RM_3M','RM_6M']].groupby('Industry').mean()
    rs_sector = rs_sector.sort_values('Relative Strength', ascending=False)
    rs_sector2 = rs_sector.reset_index(drop=False)

    rs_sector2['Rank'] = rs_sector2.index + 1

    calculate_percentile(rs_sector2, 'Relative Strength', 'Percentile')
    calculate_percentile(rs_sector2, 'RS_1W', '1 Week Ago')
    calculate_percentile(rs_sector2, 'RS_1M', '1 Month Ago')
    calculate_percentile(rs_sector2, 'RS_3M', '3 Months Ago')
    calculate_percentile(rs_sector2, 'RS_6M', '6 Months Ago')

    rs_sector2['Diff'] = rs_sector2['Relative Strength'] - rs_sector2['RS_1W']

    rs_sector2['Tickers'] = ""
    for sector_name in rs_sector2['Industry']:
        tickers_str = ','.join(rs_result2[rs_result2['Industry'] == sector_name]['Ticker'].tolist())
        rs_sector2.loc[rs_sector2['Industry'] == sector_name, 'Tickers'] = tickers_str

    rs_sector2 = rs_sector2.set_index('Rank', drop=True)

    rs_result2.drop(['RS_1W','RS_1M','RS_3M','RS_6M'], axis=1, inplace=True)
    rs_sector2.drop(['RS_1W','RS_1M','RS_3M','RS_6M'], axis=1, inplace=True)

    rs_result2.to_csv(rs_result_csv)
    rs_sector2.to_csv(rs_sector_csv)

    return