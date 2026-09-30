import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    APP_NAME: str = "Stock Prediction & News Sentiment Analysis"
    API_V1_STR: str = "/api"
    
    # Stock Market & News API Keys
    ALPHA_VANTAGE_API_KEY: Optional[str] = "demo"
    NEWS_API_KEY: Optional[str] = ""
    
    # Database URL
    DATABASE_URL: str = "sqlite:///./stock_prediction.db"
    
    # Model parameters
    LOOKBACK_WINDOW: int = 60
    LSTM_EPOCHS: int = 25
    LSTM_BATCH_SIZE: int = 16
    FINBERT_MODEL: str = "ProsusAI/finbert"
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
