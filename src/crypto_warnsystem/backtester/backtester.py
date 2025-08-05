# backtester.py

import pandas as pd
from data_utils import get_klines
from indicator_utils import calculate_indicators
from prediction_model import predict_future_direction

from datetime import timedelta

SYMBOL = "BTCUSDT"
INTERVAL = "1h"
BACKTEST_HOURS = 72  # letzte 72 Stunden

print("🔁 Backtesting wird durchgeführt...\n")

# Holt längere Historie
df = get_klines(SYMBOL, interval=INTERVAL, lookback=BACKTEST_HOURS)
df = calculate_indicators(df)

results = []
window_size = 24  # in Stunden
step_size = 4     # wie oft Prognosen gemacht werden (alle 4h)

for i in range(window_size, len(df) - step_size):
    subset = df.iloc[i - window_size:i]  # Letzte X Stunden als Input
    future = df.iloc[i + step_size]["close"]  # Kurs in +4h
    current = df.iloc[i]["close"]

    true_direction = 1 if future > current else 0

    prediction = predict_future_direction(subset)
    if prediction:
        pred_direction = prediction["direction"]
        confidence = prediction["confidence"]

        results.append({
            "Zeitpunkt": df.index[i],
            "Wahr": true_direction,
            "Vorhersage": pred_direction,
            "Confidence": confidence
        })

# Auswertung
results_df = pd.DataFrame(results)
treffer = (results_df["Wahr"] == results_df["Vorhersage"]).sum()
gesamt = len(results_df)
quote = (treffer / gesamt) * 100 if gesamt > 0 else 0

print(f"✅ Backtest abgeschlossen für {SYMBOL}")
print(f"➡️ Trefferquote: {quote:.2f}% ({treffer} von {gesamt})")

# Optional speichern
results_df.to_csv("backtest_results.csv", index=False)
