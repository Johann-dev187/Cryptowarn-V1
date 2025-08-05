# logger_utils.py

import logging
import os
from datetime import datetime

# Log-Verzeichnis erstellen
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

# Log-Dateiname mit Datum
log_filename = os.path.join(log_dir, f"log_{datetime.now().strftime('%Y%m%d')}.log")

def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        # Konsole
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
        console_handler.setFormatter(console_format)

        # Datei
        file_handler = logging.FileHandler(log_filename)
        file_handler.setLevel(logging.INFO)
        file_format = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
        file_handler.setFormatter(file_format)

        # Hinzufügen
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    return logger
