
import argparse
import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Projektpfad einfügen
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from utils.data_utils import get_klines
from utils.indicator_utils import calculate_indicators

def detect_liquidity_levels(df, window=10):
    highs = df['high'].rolling(window, center=True).max()
    lows = df['low'].rolling(window, center=True).min()
    levels = []

    for i in range(window, len(df) - window):
        is_swing_high = df['high'][i] == highs[i]
        is_swing_low = df['low'][i] == lows[i]
        if is_swing_high:
            levels.append((df.index[i], df['high'][i], 'high'))
        if is_swing_low:
            levels.append((df.index[i], df['low'][i], 'low'))
    return levels

def backtest_rsi_liquidity(df, levels, rsi_col='rsi', buy_threshold=30, sell_threshold=70):
    position = None
    entry_price = 0
    trades = []

    for i in range(1, len(df)):
        price = df['close'].iloc[i]
        rsi = df[rsi_col].iloc[i]
        time = df.index[i]

        if position is None and rsi < buy_threshold:
            for lvl_time, lvl_price, lvl_type in levels:
                if lvl_type == 'low' and abs(price - lvl_price) / lvl_price < 0.005:
                    position = 'long'
                    entry_price = price
                    trades.append((time, 'BUY', price))
                    break

        elif position == 'long' and rsi > sell_threshold:
            for lvl_time, lvl_price, lvl_type in levels:
                if lvl_type == 'high' and abs(price - lvl_price) / lvl_price < 0.005:
                    trades.append((time, 'SELL', price))
                    position = None
                    break

    return trades

def plot_trades(df, trades):
    plt.figure(figsize=(12, 6))
    plt.plot(df.index, df['close'], label='Close Price')
    for t in trades:
        color = 'green' if t[1] == 'BUY' else 'red'
        plt.scatter(t[0], t[2], color=color, label=t[1], marker='^' if t[1] == 'BUY' else 'v')
    plt.title("Backtest - RSI + Liquidity Levels")
    plt.legend()
    plt.grid()
    plt.show()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--symbol', type=str, default='BTCUSDT')
    parser.add_argument('--interval', type=str, default='1h')
    parser.add_argument('--lookback', type=str, default='60 day ago UTC')
    args = parser.parse_args()

    df = get_klines(symbol=args.symbol, interval=args.interval, lookback=args.lookback)
    df = calculate_indicators(df)

    levels = detect_liquidity_levels(df)
    trades = backtest_rsi_liquidity(df, levels)

    print(f"🔍 {len(trades)//2} abgeschlossene Trades gefunden.")
    wins = 0
    for i in range(0, len(trades)-1, 2):
        buy_price = trades[i][2]
        sell_price = trades[i+1][2]
        pnl = sell_price - buy_price
        if pnl > 0:
            wins += 1
    if trades:
        print(f"📈 Gewinnquote: {wins / (len(trades)//2) * 100:.2f}%")
    plot_trades(df, trades)

if __name__ == "__main__":
    main()
