# --------------------------------------------- #
# Relative Strength計算ライブラリ
# --------------------------------------------- #
import pandas as pd
from datetime import datetime, timedelta

# --------------------------------------------- #
# Relative Strengthの計算
# --------------------------------------------- #
def calculate_relative_strength(history):
    # Relative Strengthを計算
    try:
        c    = history["Close"].iloc[-1]
    except IndexError:
        c    = history["Close"].iloc[0] if not history.empty else 0

    try:
        c63  = history["Close"].iloc[-63]
    except IndexError:
        c63  = history["Close"].iloc[0] if not history.empty else 0

    try:
        c126 = history["Close"].iloc[-126]
    except IndexError:
        c126 = history["Close"].iloc[0] if not history.empty else 0

    try:
        c189 = history["Close"].iloc[-189]
    except IndexError:
        c189 = history["Close"].iloc[0] if not history.empty else 0

    try:
        c252 = history["Close"].iloc[-252]
    except IndexError:
        c252 = history["Close"].iloc[0] if not history.empty else 0

    if c63 == 0 or c126 == 0 or c189 == 0 or c252 == 0:
        return 0

    rs_c63 = ((c - c63) / c63) if c63 != 0 else 0
    rs_c126 = ((c - c126) / c126) if c126 != 0 else 0
    rs_c189 = ((c - c189) / c189) if c189 != 0 else 0
    rs_c252 = ((c - c252) / c252) if c252 != 0 else 0

    relative_strength = ((rs_c63 * 0.4) + (rs_c126 * 0.2) + (rs_c189 * 0.2) + (rs_c252 * 0.2)) * 100
    return round(relative_strength, 2)


# --------------------------------------------- #
# パーセンタイル計算関数
# --------------------------------------------- #
def calculate_percentile(df, column_name1, column_name2):
    df[column_name1] = pd.to_numeric(df[column_name1], errors='coerce').fillna(0)
    total_rows = len(df)
    if total_rows > 1:
        df[column_name2] = (df[column_name1].rank(ascending=True, method='average') - 1) / (total_rows - 1) * 100
    else:
        df[column_name2] = 100
    df[column_name2] = df[column_name2].round().clip(1, 99).astype(int)
    return df


# --------------------------------------------- #
# RS Momentum計算関数
# --------------------------------------------- #
def calculate_rs_momentum(data):
    if data.empty or 'Close' not in data.columns:
        return 0
    n = 14
    close = data['Close']
    delta = close.diff()
    gain =  delta.where(delta > 0, 0).fillna(0)
    loss = -delta.where(delta < 0, 0).fillna(0)
    avg_gain = gain.rolling(window=n, min_periods=1).mean()
    avg_loss = loss.rolling(window=n, min_periods=1).mean()
    if avg_loss.iloc[-1] == 0:
        return 1.0 # If no loss, RS is infinite, RM is 1
    rs = avg_gain / avg_loss
    rs_momentum = round(rs / (1 + rs), 2)
    return rs_momentum.iloc[-1]


# --------------------------------------------- #
# RS計算処理関数
# --------------------------------------------- #
def calc_rs(stock_codes, all_history, rs_result_csv, rs_sector_csv):

    print("Starting RS calculation...")
    now = datetime.now()
    W1_ago = now - timedelta(days=7)
    M1_ago = now - timedelta(days=30)
    M3_ago = now - timedelta(days=90)
    M6_ago = now - timedelta(days=180)

    results_list = []
    for index, row in stock_codes.iterrows():
        code = row['Ticker']
        sector = row['Industry']

        try:
            if isinstance(all_history.columns, pd.MultiIndex):
                if code not in all_history.columns.get_level_values(1):
                    continue
                history = all_history.xs(code, level=1, axis=1).copy()
            else:
                if len(stock_codes['Ticker'].unique()) == 1:
                    history = all_history.copy()
                else:
                    continue

            if history.empty or 'Close' not in history.columns or history['Close'].isnull().all():
                continue

            history['Close'] = history['Close'].ffill()
            if history['Close'].isnull().all():
                continue

            if len(history.loc[history.index >= W1_ago]) == 0:
                continue

            history_1w = history.loc[history.index <= W1_ago]
            history_1m = history.loc[history.index <= M1_ago]
            history_3m = history.loc[history.index <= M3_ago]
            history_6m = history.loc[history.index <= M6_ago]

            relative_strength_0 = calculate_relative_strength(history)
            if relative_strength_0 >= 2000:
                print(f"# Skip  (Code={code}): relative_strength_0 is {relative_strength_0}")
                continue

            results_list.append({
                "Industry": sector, "Ticker": code, "Relative Strength": relative_strength_0,
                "RS_1W": calculate_relative_strength(history_1w),
                "RS_1M": calculate_relative_strength(history_1m),
                "RS_3M": calculate_relative_strength(history_3m),
                "RS_6M": calculate_relative_strength(history_6m),
                "RS Momentum": calculate_rs_momentum(history),
                "RM_1W": calculate_rs_momentum(history_1w),
                "RM_1M": calculate_rs_momentum(history_1m),
                "RM_3M": calculate_rs_momentum(history_3m),
                "RM_6M": calculate_rs_momentum(history_6m)
            })

        except Exception as e:
            print(f"# Error processing {code}: {e}")
            continue

    if not results_list:
        print("No tickers were processed successfully. Exiting.")
        return

    rs_result = pd.DataFrame(results_list)

    percentile_cols = {
        'Relative Strength': 'Percentile', 'RS_1W': '1 Week Ago', 'RS_1M': '1 Month Ago',
        'RS_3M': '3 Months Ago', 'RS_6M': '6 Months Ago'
    }
    for data_col, percentile_col in percentile_cols.items():
        rs_result = calculate_percentile(rs_result, data_col, percentile_col)

    rs_result['Diff'] = rs_result['Relative Strength'] - rs_result['RS_1W']
    rs_result.sort_values('Relative Strength', ascending=False, inplace=True)
    rs_result.reset_index(drop=True, inplace=True)
    rs_result['Rank'] = range(1, len(rs_result) + 1)

    # Industry calculations
    industry_cols = ['Industry', 'Relative Strength', 'Diff', 'RS_1W', 'RS_1M', 'RS_3M', 'RS_6M',
                     'RS Momentum', 'RM_1W', 'RM_1M', 'RM_3M', 'RM_6M']
    rs_sector = rs_result[industry_cols].groupby('Industry').mean()
    rs_sector.sort_values('Relative Strength', ascending=False, inplace=True)
    rs_sector.reset_index(inplace=True)
    rs_sector['Rank'] = range(1, len(rs_sector) + 1)

    for data_col, percentile_col in percentile_cols.items():
        rs_sector = calculate_percentile(rs_sector, data_col, percentile_col)

    tickers_by_industry = rs_result.groupby('Industry')['Ticker'].apply(lambda x: ','.join(x)).reset_index(name='Tickers')
    rs_sector = pd.merge(rs_sector, tickers_by_industry, on='Industry')

    # Final cleanup and save
    cols_to_drop = ['RS_1W', 'RS_1M', 'RS_3M', 'RS_6M']
    rs_result.drop(columns=cols_to_drop, inplace=True)
    rs_sector.drop(columns=cols_to_drop, inplace=True)

    rs_result.set_index('Rank', inplace=True)
    rs_sector.set_index('Rank', inplace=True)

    rs_result.to_csv(rs_result_csv)
    rs_sector.to_csv(rs_sector_csv)
    print("Calculation complete. Results saved.")
    return
