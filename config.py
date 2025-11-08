"""Configuration management for Binance Thailand Trading Bot."""

import os
from typing import List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration."""

    # Binance API Configuration
    BINANCE_API_KEY: str = os.getenv("BINANCE_API_KEY", "")
    BINANCE_API_SECRET: str = os.getenv("BINANCE_API_SECRET", "")
    BINANCE_BASE_URL: str = os.getenv("BINANCE_BASE_URL", "https://api.binance.th")

    # Slack Configuration
    SLACK_WEBHOOK_URL: str = os.getenv("SLACK_WEBHOOK_URL", "")

    # Trading Configuration
    CHECK_INTERVAL_HOURS: int = int(os.getenv("CHECK_INTERVAL_HOURS", "1"))
    SYMBOLS: List[str] = os.getenv("SYMBOLS", "BTC/THB,ETH/THB").split(",")

    # RSI Configuration
    RSI_LENGTH: int = int(os.getenv("RSI_LENGTH", "14"))
    RSI_OVERSOLD: float = float(os.getenv("RSI_OVERSOLD", "30"))
    RSI_OVERBOUGHT: float = float(os.getenv("RSI_OVERBOUGHT", "70"))

    # MACD Configuration
    MACD_FAST: int = int(os.getenv("MACD_FAST", "12"))
    MACD_SLOW: int = int(os.getenv("MACD_SLOW", "26"))
    MACD_SIGNAL: int = int(os.getenv("MACD_SIGNAL", "9"))

    # Trading Settings
    ENABLE_AUTO_TRADE: bool = os.getenv("ENABLE_AUTO_TRADE", "false").lower() == "true"

    # Data Storage
    DATA_DIR: str = "data"
    PORTFOLIO_FILE: str = os.path.join(DATA_DIR, "portfolio.json")
    HISTORY_FILE: str = os.path.join(DATA_DIR, "history.json")

    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration."""
        if not cls.BINANCE_API_KEY or not cls.BINANCE_API_SECRET:
            raise ValueError("Binance API credentials are required")
        if not cls.SLACK_WEBHOOK_URL:
            raise ValueError("Slack webhook URL is required")
        return True


# Create data directory if it doesn't exist
os.makedirs(Config.DATA_DIR, exist_ok=True)
