import argparse
import os
import sys
import pandas as pd
import matplotlib.pyplot as plt

# Project root so that "import crypto_warnsystem" works
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from crypto_warnsystem.utils.data_utils import get_klines
from crypto_warnsystem.utils.indicator_utils import calculate_indicators, calculate_liquidity_levels

def backtest_rsi_liquidity(
    df: pd.DataFrame,
    levels: pd.Series,
    buy_threshold: float = 30,
    sell_threshold: float = 70,
    rsi_col: str = 'rsi'
) -> list:
    """
    Backtest mit RSI-Signalen kombiniert mit Liquidity Levels.
    Buy, wenn RSI < buy_threshold und Kurs < Liquidity-Level.
    Sell, wenn RSI > sell_threshold und Kurs > Liquidity-Level.
    """
    position = None
    trades = []

    for i in range(1, len(df)):
        price = df['close'].iloc[i]
        rsi = df[rsi_col].iloc[i]
        lvl = levels.iloc[i]
        time = df.index[i]

        if position is None:
            if pd.notna(lvl) and rsi < buy_threshold and price < lvl:
                position = 'long'
                trades.append((time, 'BUY', price))
        else:
            if pd.notna(lvl) and rsi > sell_threshold and price > lvl:
                trades.append((time, 'SELL', price))
                position = None

    return trades

def plot_trades(df: pd.DataFrame, trades: list):
    """
    Plotte die Backtest-Trades auf dem Kurschart.
    """
    plt.figure(figsize=(12, 6))
    plt.plot(df.index, df['close'], label='Close Price')
    for t in trades:
        marker = '^' if t[1] == 'BUY' else 'v'
        color = 'green' if t[1] == 'BUY' else 'red'
        plt.scatter(t[0], t[2], marker=marker, color=color)
    plt.title("Backtest - RSI + Liquidity Levels")
    plt.legend()
    plt.grid()
    plt.show()

def main():
    parser = argparse.ArgumentParser(
        description="Run backtest for RSI + Liquidity Levels strategy"
    )
    parser.add_argument(
        '--symbol', type=str, default='BTCUSDT',
        help='Trading symbol, e.g., BTCUSDT'
    )
    parser.add_argument(
        '--interval', type=str, default='1h',
        help='Kline interval, e.g., 1h, 4h'
    )
    parser.add_argument(
        '--lookback', type=str, default='60 day ago UTC',
        help='Lookback period, e.g., 60 day ago UTC'
    )
    args = parser.parse_args()

    df = get_klines(symbol=args.symbol, interval=args.interval, lookback=args.lookback)
    df = calculate_indicators(df)

    levels = calculate_liquidity_levels(df, window=20)
    trades = backtest_rsi_liquidity(df, levels)

    print(f"🔍 {len(trades)//2} abgeschlossene Trades gefunden.")
    wins = sum(
        1 for i in range(0, len(trades)-1, 2)
        if trades[i+1][2] - trades[i][2] > 0
    )
    total = max(len(trades)//2, 1)
    print(f"📈 Gewinnquote: {wins/total*100:.2f}%")

    plot_trades(df, trades)

if __name__ == "__main__":
    main()
