import pandas as pd
import pytest

from src.crypto_warnsystem.utils.data_utils import get_klines

def test_get_klines_returns_dataframe():
    df = get_klines(symbol="BTCUSDT", interval="1m", lookback="1 hour ago UTC")
    assert isinstance(df, pd.DataFrame)

def test_get_klines_empty_on_dummy():
    # Simuliere fehlgeschlagenen Binance-Client: setze ungültige Keys
    import os
    os.environ["BINANCE_API_KEY"] = "invalid"
    os.environ["BINANCE_API_SECRET"] = "invalid"
    df = get_klines(symbol="BTCUSDT", interval="1m", lookback="1 hour ago UTC")
    # DummyClient liefert leeren DataFrame
    assert df.empty
