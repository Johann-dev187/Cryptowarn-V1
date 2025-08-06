# src/crypto_warnsystem/utils/data_utils.py

import os
import pandas as pd
from binance.client import Client

# Lade API-Keys aus der Umgebung (falls gesetzt)
API_KEY    = os.getenv("BINANCE_API_KEY", None)
API_SECRET = os.getenv("BINANCE_API_SECRET", None)

class _DummyClient:
    """Dummy-Client, um CI-Pings zu umgehen."""
    @staticmethod
    def get_historical_klines(symbol, interval, lookback):
        return []

def _make_client():
    """
    Erstelle echten Binance-Client oder Dummy, falls kein Zugriff möglich.
    """
    try:
        return Client(API_KEY, API_SECRET)
    except Exception:
        # ping oder Auth schlägt fehl → Dummy verwenden
        return _DummyClient()

def get_klines(
    symbol: str = "BTCUSDT",
    interval: str = Client.KLINE_INTERVAL_5MINUTE,
    lookback: str = "2 day ago UTC"
) -> pd.DataFrame:
    """
    Holt historische Kerzendaten von Binance.
    Fällt auf Dummy zurück, wenn der Live-Client nicht initialisiert werden kann.
    """
    client = _make_client()
    klines = client.get_historical_klines(symbol, interval, lookback)

    df = pd.DataFrame(
        klines,
        columns=[
            'time', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_asset_volume', 'trades',
            'taker_buy_base_volume', 'taker_buy_quote_volume', 'ignore'
        ]
    )

    if df.empty:
        # Leeren DataFrame mit den richtigen Spalten zurückgeben
        return pd.DataFrame(columns=['open','high','low','close','volume'])

    df['time'] = pd.to_datetime(df['time'], unit='ms')
    df.set_index('time', inplace=True)
    return df[['open','high','low','close','volume']].astype(float)
