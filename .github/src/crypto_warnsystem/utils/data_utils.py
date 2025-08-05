import pandas as pd
from binance.client import Client
import datetime

client = Client()  # Ohne API-Key für öffentliche Daten

def get_klines(symbol="BTCUSDT", interval=Client.KLINE_INTERVAL_5MINUTE, lookback="2 day ago UTC"):
    """
    Holt historische Kerzendaten von Binance.

    :param symbol: z. B. 'BTCUSDT'
    :param interval: Binance-Interval-Konstante
    :param lookback: Zeitspanne (z. B. "1 day ago UTC")
    :return: DataFrame mit OHLCV-Daten
    """
    klines = client.get_historical_klines(symbol, interval, lookback)

    df = pd.DataFrame(klines, columns=[
        'time', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'trades',
        'taker_buy_base_volume', 'taker_buy_quote_volume', 'ignore'
    ])

    df['time'] = pd.to_datetime(df['time'], unit='ms')
    df.set_index('time', inplace=True)
    df = df[['open', 'high', 'low', 'close', 'volume']].astype(float)

    return df
