import requests
import os
from dotenv import load_dotenv

load_dotenv()

def send_message(chat_id: str, text: str):
    """Sendet eine Nachricht an einen Telegram-Chat."""
    token = os.getenv("TELEGRAM_TOKEN")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
    except Exception as e:
        print(f"❌ Fehler beim Senden an Telegram: {e}")

def send_telegram(text: str):
    """Vereinfachter Aufruf mit Standard-Chat-ID."""
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    send_message(chat_id, text)
