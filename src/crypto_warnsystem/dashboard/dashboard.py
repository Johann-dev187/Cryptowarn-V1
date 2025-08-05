# coding: utf-8
import streamlit as st
import logging
import os
from datetime import datetime

import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv

# Eigene Module
from utils.data_utils import get_klines
from utils.indicator_utils import calculate_indicators
from models.prediction_model import predict_future_direction
from utils.messaging_utils import send_telegram

# === Logging konfigurieren ===
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# === .env laden ===
load_dotenv()
DEFAULT_PRICE_DROP = int(os.getenv("PRICE_DROP_THRESHOLD", 3))
DEFAULT_RSI_OVERBOUGHT = int(os.getenv("RSI_OVERBOUGHT", 70))
DEFAULT_RSI_OVERSOLD = int(os.getenv("RSI_OVERSOLD", 30))

# === GUI ===
st.set_page_config(page_title="Crypto Warnsystem", layout="wide")
st.title("📈 Crypto-Frühwarnsystem Dashboard")
st.markdown("Live-Datenanalyse + Telegram-Alarmierung")

# Coin-Auswahl
symbol = st.selectbox("Wähle Coin-Paar:", ["BTCUSDT", "ETHUSDT", "SOLUSDT"])

# Schwellenwerte einstellbar (laden aus .env als Defaultwerte)
st.sidebar.header("🔧 Einstellungen")
price_drop_threshold = st.sidebar.slider("🔻 Preis-Sturz-Schwelle (%)", 1, 20, DEFAULT_PRICE_DROP)
rsi_overbought = st.sidebar.slider("📈 RSI überkauft ab", 60, 90, DEFAULT_RSI_OVERBOUGHT)
rsi_oversold = st.sidebar.slider("📉 RSI überverkauft ab", 10, 50, DEFAULT_RSI_OVERSOLD)

# Daten abrufen und Indikatoren berechnen
df = get_klines(symbol)
df = calculate_indicators(df)

# Aktuelle Werte
last = df.iloc[-1]
previous = df.iloc[-2]

drop_pct = (previous['close'] - last['close']) / previous['close']

st.metric("📊 Aktueller Preis", f"{last['close']:.2f} USD")
st.metric("📉 RSI", f"{last['rsi']:.2f}")
st.metric("📈 MACD", f"{last['macd']:.4f}")

# Warnlogik
alerts = []
trade_signals = []
signal_log = []

# === Scoring-System ===
score = 0
if drop_pct >= price_drop_threshold / 100:
    alerts.append(f"🚨 Preissturz: {symbol} fiel um {drop_pct*100:.2f}%")
    score += 2
if last['rsi'] >= rsi_overbought:
    alerts.append(f"📈 RSI überkauft: {last['rsi']:.2f}")
    signal_log.append((datetime.now(), symbol, "Verkauf", "RSI überkauft"))
    trade_signals.append("💡 Mögliche Verkaufsgelegenheit (RSI überkauft)")
    score -= 1
elif last['rsi'] <= rsi_oversold:
    alerts.append(f"📉 RSI überverkauft: {last['rsi']:.2f}")
    signal_log.append((datetime.now(), symbol, "Kauf", "RSI überverkauft"))
    trade_signals.append("💰 Mögliche Kaufgelegenheit (RSI überverkauft)")
    score += 2
if last['macd'] > 0 and previous['macd'] < 0:
    alerts.append("🟢 MACD Crossover: Aufwärtstrend")
    signal_log.append((datetime.now(), symbol, "Kauf", "MACD Crossover oben"))
    trade_signals.append("💰 Mögliche Kaufgelegenheit (MACD Crossover nach oben)")
    score += 2
elif last['macd'] < 0 and previous['macd'] > 0:
    alerts.append("🔴 MACD Crossover: Abwärtstrend")
    signal_log.append((datetime.now(), symbol, "Verkauf", "MACD Crossover unten"))
    trade_signals.append("⚠️ Mögliche Verkaufsgelegenheit (MACD Crossover nach unten)")
    score -= 2

st.subheader("📈 Gesamtscore")
st.metric("Handelsscore", score)

# ML-Prognose (4h Vorhersage)
st.subheader("🔮 4h Prognose basierend auf historischem ML-Modell")
prediction_result = predict_future_direction(df)

if prediction_result:
    col1, col2 = st.columns(2)
    with col1:
        st.metric("📈 Prognose", "Steigt" if prediction_result["direction"] == 1 else "Fällt/Seitwärts")
    with col2:
        st.metric("🔐 Vertrauen", f"{prediction_result['confidence']*100:.1f}%")

    st.caption(f"Modell-Version: {prediction_result.get('model_version', '?')}")

    st.subheader("🔄 Wahrscheinlichkeiten der ML-Prognose")
    chart_data = pd.DataFrame({
        'Prognose': ['Fällt', 'Steigt'],
        'Wahrscheinlichkeit': [prediction_result['proba']['fall'], prediction_result['proba']['rise']]
    })
    st.bar_chart(chart_data.set_index('Prognose'))

    # Prognoseverlauf speichern
    history_path = "prognose_history.csv"
    new_entry = {
        "timestamp": datetime.now(),
        "direction": prediction_result["direction"],
        "confidence": prediction_result["confidence"]
    }
    history_df = pd.DataFrame([new_entry])
    if os.path.exists(history_path):
        old_df = pd.read_csv(history_path)
        old_df = pd.concat([old_df, history_df], ignore_index=True)
    else:
        old_df = history_df
    old_df.to_csv(history_path, index=False)

    # Telegram-Meldung senden
    try:
        if prediction_result['direction'] == 1:
            st.success("📈 ML-Prognose: Markt könnte steigen")
            send_telegram(f"📣 Prognose: {symbol} wird in den nächsten 4h wahrscheinlich steigen. Vertrauen: {prediction_result['confidence']*100:.1f}%")
        else:
            st.error("📉 ML-Prognose: Markt könnte fallen oder seitwärts laufen")
            send_telegram(f"📣 Prognose: {symbol} wird in den nächsten 4h wahrscheinlich fallen/seitwärts. Vertrauen: {prediction_result['confidence']*100:.1f}%")
    except Exception as e:
        logging.warning(f"Telegram-Versand fehlgeschlagen: {e}")
else:
    st.warning("Keine Vorhersage verfügbar – möglicherweise unzureichende Daten.")

# Trendverlauf
if os.path.exists("prognose_history.csv"):
    st.subheader("📉 Prognose-Trendverlauf (letzte 24h)")
    df_hist = pd.read_csv("prognose_history.csv")
    df_hist["timestamp"] = pd.to_datetime(df_hist["timestamp"])
    df_hist = df_hist[df_hist["timestamp"] >= datetime.now() - pd.Timedelta(hours=24)]

    fig2, ax2 = plt.subplots()
    ax2.plot(df_hist["timestamp"], df_hist["confidence"], label="Confidence", color="green")
    ax2.set_ylabel("Confidence")
    ax2.set_title("Confidence-Verlauf")
    ax2.legend()
    st.pyplot(fig2)

# Preisdiagramm
fig, ax = plt.subplots(figsize=(12, 5))
df[-150:]['close'].plot(ax=ax, label='Preis', alpha=0.6)
df[-150:]['sma50'].plot(ax=ax, label='SMA 50', linestyle='--')
df[-150:]['sma200'].plot(ax=ax, label='SMA 200', linestyle='--')
df[-150:]['bb_upper'].plot(ax=ax, label='Bollinger High', linestyle=':')
df[-150:]['bb_lower'].plot(ax=ax, label='Bollinger Low', linestyle=':')
ax.set_title(f"Preis + SMA + Bollinger ({symbol})")
ax.legend()
st.pyplot(fig)

# Alarme anzeigen
st.subheader("🚨 Aktive Alarme")
if alerts:
    for alert in alerts:
        st.error(alert)
else:
    st.success("Keine aktiven Alarme")

# Handelsideen anzeigen
st.subheader("💡 Handelsideen")
if trade_signals:
    for signal in trade_signals:
        st.info(signal)
        send_telegram(f"📈 {symbol} Signal: {signal}")
else:
    st.text("Keine aktuellen Kauf-/Verkaufssignale")

# Signal-Historie anzeigen
st.subheader("📄 Signal-Historie (letzte Auswertung)")
if signal_log:
    history_df = pd.DataFrame(signal_log, columns=["Zeit", "Symbol", "Aktion", "Begründung"])
    st.dataframe(history_df)
else:
    st.caption("Keine Signale im aktuellen Durchlauf erkannt.")

# Telegram-Testknopf
if st.button("📤 Telegram-Testnachricht senden"):
    send_telegram(f"📣 Test: Das Crypto-Dashboard ist verbunden! (Aktiv: {symbol})")
    st.toast("Nachricht gesendet!")

# Preisverlauf
st.subheader(f"📉 Preisverlauf für {symbol}")
st.line_chart(df['close'])
