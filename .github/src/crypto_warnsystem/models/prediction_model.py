# prediction_model.py

import pandas as pd
import joblib
import os

MODEL_PATH = "model/trained_model.pkl"

def predict_future_direction(df: pd.DataFrame):
    """
    Nutzt das trainierte Modell, um die Kursrichtung vorherzusagen.

    Gibt ein Dict mit Richtung, Vertrauen und Wahrscheinlichkeiten zurück.
    """

    if not os.path.exists(MODEL_PATH):
        print("⚠️ Kein Modell gefunden.")
        return None

    try:
        model = joblib.load(MODEL_PATH)
    except Exception as e:
        print(f"Fehler beim Laden des Modells: {e}")
        return None

    # Letzte Zeile (aktuelle Werte)
    last = df.iloc[-1]

    # Features, wie im Training
    features = pd.DataFrame([{
        "rsi": last["rsi"],
        "macd": last["macd"],
        "bb_upper": last["bb_upper"],
        "bb_lower": last["bb_lower"],
        "sma50": last["sma50"],
        "sma200": last["sma200"],
        "close": last["close"]
    }])

    proba = model.predict_proba(features)[0]
    predicted_direction = model.predict(features)[0]
    confidence = max(proba)

    return {
        "direction": int(predicted_direction),  # 1 = steigt, 0 = fällt/seitwärts
        "confidence": confidence,
        "proba": {
            "fall": proba[0],
            "rise": proba[1]
        },
        "model_version": "v1.0"
    }
