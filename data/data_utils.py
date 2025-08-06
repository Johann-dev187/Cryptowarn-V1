# data_utils.py

import os
import pandas as pd
from binance.client import Client

# Lade API-Keys aus der Umgebung (falls gesetzt)
API_KEY = os.getenv("BINANCE_API_KEY", None)
API_SECRET = os.getenv("BINANCE_API_SECRET", None)

def get_klines(
    symbol: str = "BTCUSDT",
    interval: str = Client.KLINE_INTERVAL_5MINUTE,
    lookback: str = "2 day ago UTC"
) -> pd.DataFrame:
    """
    Holt historische Kerzendaten von Binance.

    :param symbol: z. B. 'BTCUSDT'
    :param interval: Binance-Interval-Konstante
    :param lookback: Lookback-String, z. B. "1 day ago UTC"
    :return: DataFrame mit OHLCV-Daten
    """
    # Client erst hier erzeugen, damit kein Ping in Modul-Scope ausgeführt wird
    client = Client(API_KEY, API_SECRET)
    
    # Historische Kerzen abrufen
    klines = client.get_historical_klines(symbol, interval, lookback)

    # In DataFrame umwandeln
    df = pd.DataFrame(
        klines,
        columns=[
            'time', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_asset_volume', 'trades',
            'taker_buy_base_volume', 'taker_buy_quote_volume', 'ignore'
        ]
    )

    # Zeitstempel umwandeln und Index setzen
    df['time'] = pd.to_datetime(df['time'], unit='ms')
    df.set_index('time', inplace=True)

    # Nur die relevanten Spalten behalten und in float casten
    df = df[['open', 'high', 'low', 'close', 'volume']].astype(float)

    return df
