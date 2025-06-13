import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    ALPACA_API_KEY = os.getenv("ALPACA_API_KEY", "")
    ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY", "")
    ALPACA_BASE_URL = "https://paper-api.alpaca.markets"

    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

    CONFIDENCE_THRESHOLD = 6
    CHECK_INTERVAL_VOLATILE = 300
    CHECK_INTERVAL_SLOW = 180
    MAX_TRADES_PER_DAY = 10
    COOLDOWN_MINUTES = 3

    RSI_PERIOD = 14
    MACD_FAST = 12
    MACD_SLOW = 26
    MACD_SIGNAL = 9
    BOLLINGER_PERIOD = 20
    BOLLINGER_STD = 2.0
    VOLUME_LOOKBACK = 20
    VOLUME_THRESHOLD = 2.0 