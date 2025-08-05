# telegram_command_bot.py

import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import time
import logging
import requests
from dotenv import load_dotenv
from models.prediction_model import predict_future_direction
from utils.data_utils import get_klines
from utils.messaging_utils import send_message
import telebot

# === Projektpfad einbinden ===
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# === Umgebungsvariablen laden ===
load_dotenv()

# === Bot initialisieren ===
bot = telebot.TeleBot(os.getenv("TELEGRAM_TOKEN"))

# === Befehle verarbeiten ===
def handle_command(command, chat_id):
    print(f"📨 Befehl empfangen: {command} von {chat_id}")
    
    if command == "/start":
        send_message(chat_id, "👋 Willkommen beim Crypto-Warn-Bot!\n\nVerfügbare Befehle:\n"
                              "/prognose – Zeigt ML-Prognose für BTC\n"
                              "/verlauf – Kursveränderung der letzten 24h\n"
                              "/hilfe – Hilfe anzeigen")
        
    elif command == "/hilfe":
        send_message(chat_id, "📘 Befehle:\n"
                              "/prognose – ML-Vorhersage für BTCUSDT\n"
                              "/verlauf – Kursveränderung 24h\n"
                              "/hilfe – Hilfe anzeigen")
        
    elif command == "/prognose":
        df = get_klines("BTCUSDT")
        result = predict_future_direction(df)
        if result:
            trend = "📈 Steigt" if result["direction"] == 1 else "📉 Fällt/Seitwärts"
            conf = f"{result['confidence'] * 100:.1f}%"
            send_message(chat_id, f"📊 Prognose (4h): {trend}\nVertrauen: {conf}")
        else:
            send_message(chat_id, "⚠️ Keine Prognose verfügbar.")
    
    elif command == "/verlauf":
        try:
            df = get_klines("BTCUSDT", interval="1h", lookback="48")
            now = df.iloc[-1]["close"]
            past = df.iloc[-24]["close"]
            change = ((now - past) / past) * 100
            emoji = "📈" if change > 0 else "📉"
            send_message(chat_id, f"{emoji} Kursveränderung (24h): {change:.2f} %")
        except Exception as e:
            send_message(chat_id, f"❌ Fehler beim Abrufen der Daten: {e}")
    
    else:
        send_message(chat_id, "❓ Unbekannter Befehl. Nutze /hilfe.")

# === Telegram-Nachrichten weiterleiten ===
@bot.message_handler(func=lambda message: True)
def route_message(message):
    print(f"📥 Nachricht empfangen: {message.text}")
    handle_command(message.text.strip().lower(), message.chat.id)

# === Start ===
print("🤖 Bot läuft und wartet auf Befehle...")
bot.polling()
