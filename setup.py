
import os
from pathlib import Path

def ask_input(prompt, default=""):
    val = input(f"{prompt} [{default}]: ").strip()
    return val if val else default

def write_env_file(env_path, values):
    with open(env_path, "w") as f:
        for key, val in values.items():
            f.write(f"{key}={val}\n")
    print(f"✅ .env-Datei gespeichert unter: {env_path}")

def main():
    print("🔧 Interaktives Setup für das Crypto-Warnsystem")
    print("------------------------------------------------")

    # Fragen
    telegram_token = ask_input("1️⃣  Telegram-Bot-Token eingeben", "DEIN_TELEGRAM_TOKEN")
    telegram_chat_id = ask_input("2️⃣  Telegram-Chat-ID eingeben", "DEINE_CHAT_ID")
    binance_key = ask_input("3️⃣  Binance API Key (optional)", "")
    binance_secret = ask_input("4️⃣  Binance API Secret (optional)", "")

    # Zielpfad
    env_path = Path(__file__).resolve().parent / ".env"

    # Speichern
    values = {
        "TELEGRAM_TOKEN": telegram_token,
        "TELEGRAM_CHAT_ID": telegram_chat_id,
        "BINANCE_API_KEY": binance_key,
        "BINANCE_API_SECRET": binance_secret
    }
    write_env_file(env_path, values)

    print("\n🚀 Du kannst das System jetzt starten!")
    print("➡️  z. B. mit:  python bot/telegram_command_bot.py  oder  streamlit run dashboard/dashboard.py")

if __name__ == "__main__":
    main()
