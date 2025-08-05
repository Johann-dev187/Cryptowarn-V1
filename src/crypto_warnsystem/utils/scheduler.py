# scheduler.py

import time
from datetime import datetime
from dotenv import load_dotenv
import os
import pandas as pd

from data_utils import get_klines
from indicator_utils import calculate_indicators
from prediction_model import predict_future_direction
from messaging_utils import send_message

# .env laden
load_dotenv()
SYMBOL = "BTCUSDT"
INTERVAL_HOURS = 4
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

print("⏳ Scheduler gestartet – prognostiziert alle 4h...")

def run_scheduler():
    while True:
        try:
            print(f"\n📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} – Prognose läuft...")
            df = get_klines(SYMBOL)
            df = calculate_indicators(df)
            prediction = predict_future_direction(df)

            if prediction:
                direction_text = "📈 Steigt" if prediction['direction'] == 1 else "📉 Fällt/Seitwärts"
                conf_text = f"{prediction['confidence'] * 100:.1f}%"
                message = f"📊 Automatische Prognose für {SYMBOL}:\n{direction_text}\nVertrauen: {conf_text}"
                send_message(TELEGRAM_CHAT_ID, message)
                print("✅ Prognose gesendet:", message)

                # Prognoseverlauf speichern
                log_path = "prognose_history.csv"
                new_entry = {
                    "timestamp": datetime.now(),
                    "direction": prediction["direction"],
                    "confidence": prediction["confidence"]
                }
                df_new = pd.DataFrame([new_entry])
                if os.path.exists(log_path):
                    df_old = pd.read_csv(log_path)
                    df_full = pd.concat([df_old, df_new], ignore_index=True)
                else:
                    df_full = df_new
                df_full.to_csv(log_path, index=False)

            else:
                warning = "⚠️ Keine Prognose generierbar (zu wenige Daten?)"
                send_message(TELEGRAM_CHAT_ID, warning)
                print(warning)

        except Exception as e:
            err_msg = f"❌ Fehler im Scheduler: {e}"
            send_message(TELEGRAM_CHAT_ID, err_msg)
            print(err_msg)

        print(f"🕒 Schlafe für {INTERVAL_HOURS} Stunden...\n")
        time.sleep(INTERVAL_HOURS * 3600)


if __name__ == "__main__":
    run_scheduler()
