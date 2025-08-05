@echo off
cd /d "%~dp0"

echo Starte Telegram-Bot...
start cmd /k python bot/telegram_command_bot.py

echo Starte Dashboard...
start cmd /k streamlit run dashboard/dashboard.py

echo Starte Scheduler...
start cmd /k python scheduler.py

pause
