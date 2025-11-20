import os
from dotenv import load_dotenv

load_dotenv()

# Основные настройки
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
DATABASE_URL = os.getenv("DATABASE_URL")
AI_TUNNEL_API_KEY = os.getenv("AITUNNEL_API_KEY")

# Мониторинг
SITES = [
    {"url": "https://example.com", "selector": "body"},
]

CHECK_INTERVAL_MINUTES = 10
LOG_FILE = "monitor.log"