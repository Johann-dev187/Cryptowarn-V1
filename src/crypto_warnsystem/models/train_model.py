# train_model.py
import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib
import os
from utils.data_utils import get_klines
from utils.indicator_utils import calculate_indicators

MODEL_DIR = "model"
MODEL_PATH = os.path.join(MODEL_DIR, "trained_model.pkl")

def label_data(df: pd.DataFrame, future_periods=12):
    """
    Erstellt Zielvariable (0 = fällt/seitwärts, 1 = steigt)
    """
    df["future_return"] = df["close"].pct_change(periods=future_periods).shift(-future_periods)
    df["target"] = (df["future_return"] > 0).astype(int)
    return df

def train_model():
    print("📊 Lade historische Daten...")
    df = get_klines("BTCUSDT", interval="15m", lookback="15 day ago UTC")
    df = calculate_indicators(df)
    df = label_data(df)

    df.dropna(inplace=True)

    features = ["rsi", "macd", "bb_upper", "bb_lower", "sma50", "sma200", "close"]
    X = df[features]
    y = df["target"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    print("🧠 Trainiere Modell...")
    model = RandomForestClassifier(n_estimators=150, max_depth=10, random_state=42)
    model.fit(X_train, y_train)

    print("✅ Training abgeschlossen. Evaluierung:")
    y_pred = model.predict(X_test)
    print(classification_report(y_test, y_pred))

    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    print(f"💾 Modell gespeichert unter: {MODEL_PATH}")

if __name__ == "__main__":
    train_model()
