"""
Configuration and environment variables for AlphaSignal
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """Application settings and environment variables"""

    # Application settings
    APP_NAME: str = "AlphaSignal - Alternative Data Alpha Research Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./alphasignal.db"
    )

    # API Keys - Alternative Data Sources
    NEWS_API_KEY: Optional[str] = os.getenv("NEWS_API_KEY", None)
    ALPHA_VANTAGE_API_KEY: Optional[str] = os.getenv("ALPHA_VANTAGE_API_KEY", None)
    REDDIT_CLIENT_ID: Optional[str] = os.getenv("REDDIT_CLIENT_ID", None)
    REDDIT_CLIENT_SECRET: Optional[str] = os.getenv("REDDIT_CLIENT_SECRET", None)
    REDDIT_USER_AGENT: str = os.getenv("REDDIT_USER_AGENT", "AlphaSignal Bot 1.0")

    # Twitter/X API (optional)
    TWITTER_API_KEY: Optional[str] = os.getenv("TWITTER_API_KEY", None)
    TWITTER_API_SECRET: Optional[str] = os.getenv("TWITTER_API_SECRET", None)
    TWITTER_BEARER_TOKEN: Optional[str] = os.getenv("TWITTER_BEARER_TOKEN", None)

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # CORS
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
    ]

    # Data Ingestion Settings
    DEFAULT_TICKERS: list = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
    NEWS_FETCH_LIMIT: int = 100  # Articles per request
    REDDIT_FETCH_LIMIT: int = 100  # Posts per request

    # ML Model Settings
    MODEL_VERSION: str = "v1.0"
    MODEL_PATH: str = os.getenv("MODEL_PATH", "./models")
    FEATURE_COUNT: int = 47

    # Technical Indicators Settings
    USE_CPP_INDICATORS: bool = os.getenv("USE_CPP_INDICATORS", "True").lower() == "true"

    # Cache Settings
    CACHE_ENABLED: bool = True
    CACHE_TTL_SECONDS: int = 3600  # 1 hour

    # Backtesting Settings
    BACKTEST_TRAIN_TEST_SPLIT: float = 0.8
    BACKTEST_MIN_CONFIDENCE: float = 0.6

    # Factor Analysis Settings
    FACTOR_LOOKBACK_DAYS: int = 252  # 1 year
    FACTOR_MIN_OBSERVATIONS: int = 30

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields from .env


# Create a global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Dependency to get settings"""
    return settings


# Helper functions for API key validation
def validate_news_api_key() -> bool:
    """Check if News API key is configured"""
    return settings.NEWS_API_KEY is not None and len(settings.NEWS_API_KEY) > 0


def validate_reddit_credentials() -> bool:
    """Check if Reddit API credentials are configured"""
    return (
        settings.REDDIT_CLIENT_ID is not None
        and settings.REDDIT_CLIENT_SECRET is not None
        and len(settings.REDDIT_CLIENT_ID) > 0
        and len(settings.REDDIT_CLIENT_SECRET) > 0
    )


def validate_alpha_vantage_key() -> bool:
    """Check if Alpha Vantage API key is configured"""
    return settings.ALPHA_VANTAGE_API_KEY is not None and len(settings.ALPHA_VANTAGE_API_KEY) > 0


def get_required_env_vars() -> dict:
    """Get a report of required environment variables and their status"""
    return {
        "NEWS_API_KEY": "✓" if validate_news_api_key() else "✗ (Optional but recommended)",
        "ALPHA_VANTAGE_API_KEY": "✓" if validate_alpha_vantage_key() else "✗ (Optional - can use yfinance)",
        "REDDIT_CLIENT_ID": "✓" if validate_reddit_credentials() else "✗ (Optional but recommended)",
        "REDDIT_CLIENT_SECRET": "✓" if validate_reddit_credentials() else "✗ (Optional but recommended)",
        "DATABASE_URL": "✓ Configured",
        "SECRET_KEY": "✓ Configured (change in production!)" if settings.SECRET_KEY != "your-secret-key-change-in-production" else "⚠ Using default (INSECURE)",
    }
