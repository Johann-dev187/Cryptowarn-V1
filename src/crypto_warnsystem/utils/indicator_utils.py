    # indicator_utils.py

import ta
import pandas as pd

def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Fügt technische Indikatoren zum DataFrame hinzu:
    - RSI
    - MACD
    - Bollinger-Bänder
    - SMA 50 & 200
    """

    close = df["close"]

    # RSI
    df["rsi"] = ta.momentum.RSIIndicator(close).rsi()

    # MACD
    df["macd"] = ta.trend.MACD(close).macd_diff()

    # Bollinger Bands
    bb = ta.volatility.BollingerBands(close)
    df["bb_upper"] = bb.bollinger_hband()
    df["bb_lower"] = bb.bollinger_lband()

    # Gleitende Durchschnitte
    df["sma50"] = close.rolling(window=50).mean()
    df["sma200"] = close.rolling(window=200).mean()

    return df

