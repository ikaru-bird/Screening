import sys
import pandas as pd
import yfinance as yf
import ta
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

def fetch_stock_data(symbol, start_date, end_date):
    stock_data = yf.download(symbol, start=start_date, end=end_date, auto_adjust=True)
    return stock_data

def calculate_technical_indicators(data):
    data['SMA_20'] = ta.trend.sma_indicator(data['Close'].squeeze(), window=20)
    data['SMA_50'] = ta.trend.sma_indicator(data['Close'].squeeze(), window=50)
    bb_indicator = ta.volatility.BollingerBands(close=data['Close'].squeeze(), window=20, window_dev=2)
    data['BB_upper'] = bb_indicator.bollinger_hband()
    data['BB_lower'] = bb_indicator.bollinger_lband()

    data['RSI'] = ta.momentum.RSIIndicator(data['Close'].squeeze(), window=14).rsi()
    macd_indicator = ta.trend.MACD(data['Close'].squeeze(), window_fast=12, window_slow=26)
    data['MACD'] = macd_indicator.macd()
    data['Signal'] = macd_indicator.macd_signal()

    return data

def assess_market_conditions(stock_data, market_name):
    # 最新のデータポイントをスカラー値として取得
    latest_close = stock_data['Close'].iloc[-1].item()
    latest_sma20 = stock_data['SMA_20'].iloc[-1].item()
    latest_sma50 = stock_data['SMA_50'].iloc[-1].item()
    latest_bb_upper = stock_data['BB_upper'].iloc[-1].item()
    latest_bb_lower = stock_data['BB_lower'].iloc[-1].item()
    latest_rsi = stock_data['RSI'].iloc[-1].item()
    latest_macd = stock_data['MACD'].iloc[-1].item()
    latest_signal = stock_data['Signal'].iloc[-1].item()

    if ((latest_close > latest_sma20) and
        (latest_close > latest_sma50) and
        (latest_sma20 > latest_sma50) and
        (latest_bb_lower < latest_close < latest_bb_upper) and
        (latest_rsi < 70) and
        (latest_macd > latest_signal)):
        market_condition = 'Investment Grade'
        signal_color = 'green'
    elif ((latest_close > latest_sma20) and
          (latest_close > latest_sma50) and
          ((latest_sma20 < latest_sma50) or
           (latest_bb_upper <= latest_close) or
           (latest_rsi >= 70) or
           (latest_macd <= latest_signal))):
        market_condition = 'Caution'
        signal_color = 'yellow'
    else:
        market_condition = 'Not Suitable for Investment'
        signal_color = 'red'

    # 判定理由を明示
    reason = ''
    if (latest_close > latest_sma20 and latest_close > latest_sma50) and \
       (latest_sma20 > latest_sma50):
        reason += '[SMA: 20/50] ::: OK\n'
    else:
        reason += '[SMA: 20/50] ::: NG\n'
    if (latest_bb_lower < latest_close < latest_bb_upper):
        reason += '[Bollinger Band] ::: OK\n'
    else:
        reason += '[Bollinger Band] ::: NG\n'
    if (latest_rsi < 70):
        reason += '[RSI] ::: OK\n'
    else:
        reason += '[RSI] ::: NG\n'
    if (latest_macd > latest_signal):
        reason += '[MACD] ::: OK'
    else:
        reason += '[MACD] ::: NG'

    # グラフを描画
    plt.figure(figsize=(10, 6))

    plt.plot(stock_data.index, stock_data['Close'], label='Close Price')
    plt.plot(stock_data.index, stock_data['SMA_20'], label='SMA 20', linestyle='--')
    plt.plot(stock_data.index, stock_data['SMA_50'], label='SMA 50', linestyle='--')
    plt.plot(stock_data.index, stock_data['BB_upper'], label='Bollinger Band Upper', linestyle=':')
    plt.plot(stock_data.index, stock_data['BB_lower'], label='Bollinger Band Lower', linestyle=':')
    plt.title(f'{market_name} Market Condition ({stock_data.index[-1].strftime("%Y-%m-%d")})')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()

    # テキストとマーカーの座標を計算
    text_x = stock_data.index[-1]
    text_y = float(latest_close - 0.05 * (stock_data['Close'].max() - stock_data['Close'].min()))
    plt.text(text_x, text_y, f'{market_condition}\n\n{reason}', ha='right', va='top', fontsize=10, bbox=dict(facecolor='white', alpha=0.5))

    # マーカーを描画
    marker_x = stock_data.index[-1]
    marker_y = float(latest_close)
    plt.scatter(marker_x, marker_y, color=signal_color, marker='o', s=100)
    plt.savefig(f'./_files/images/{market_name}_market_condition.png')
#   plt.show()

if __name__ == '__main__':

    # パラメータ受取り
    args = sys.argv
    symbol = args[1]

    # 日付のセット
    end_date = (datetime.now() + timedelta(days=1))
    start_date = end_date - timedelta(days=365)
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')

    # データの取得・処理
    stock_data = fetch_stock_data(symbol, start_date_str, end_date_str)
    stock_data = calculate_technical_indicators(stock_data)
    assess_market_conditions(stock_data, symbol)
