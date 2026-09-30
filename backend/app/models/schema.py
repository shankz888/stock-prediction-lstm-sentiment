from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Index
from datetime import datetime, timezone
from backend.app.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class StockPrice(Base):
    """Stores historical OHLCV records for tickers."""
    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(20), index=True, nullable=False)
    date = Column(String(20), index=True, nullable=False)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)

    __table_args__ = (
        Index("ix_stock_ticker_date", "ticker", "date", unique=True),
    )


class NewsArticle(Base):
    """Stores fetched and analyzed financial news articles."""
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(20), index=True, nullable=False)
    headline = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    source = Column(String(100), nullable=True)
    published_at = Column(String(30), index=True, nullable=False)
    url = Column(Text, nullable=True)
    sentiment = Column(String(20), nullable=True)          # Positive, Neutral, Negative
    sentiment_score = Column(Float, nullable=True)        # Confidence score (0.0 to 1.0)
    created_at = Column(DateTime, default=utc_now)

    __table_args__ = (
        Index("ix_news_ticker_published", "ticker", "published_at"),
    )


class Prediction(Base):
    """Stores predicted prices, metrics, and actual comparisons."""
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(20), index=True, nullable=False)
    prediction_date = Column(String(20), index=True, nullable=False)
    actual_price = Column(Float, nullable=True)
    predicted_price = Column(Float, nullable=False)
    model_version = Column(String(50), default="lstm_v1_finbert")
    mae = Column(Float, nullable=True)
    rmse = Column(Float, nullable=True)
    mape = Column(Float, nullable=True)
    created_at = Column(DateTime, default=utc_now)
