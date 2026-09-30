from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class StockQuote(BaseModel):
    company_name: str
    ticker: str
    current_price: float
    daily_change: float
    daily_change_percent: float
    volume: float
    currency: str = "USD"
    day_high: Optional[float] = None
    day_low: Optional[float] = None
    previous_close: Optional[float] = None

class OHLCVRecord(BaseModel):
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: float

class HistoricalDataResponse(BaseModel):
    ticker: str
    total_records: int
    data: List[OHLCVRecord]

class TechnicalIndicatorRecord(BaseModel):
    date: str
    close: float
    volume: float
    sma_20: Optional[float] = None
    sma_50: Optional[float] = None
    ema_12: Optional[float] = None
    ema_20: Optional[float] = None
    ema_26: Optional[float] = None
    rsi: Optional[float] = None
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    macd_hist: Optional[float] = None
    bbands_upper: Optional[float] = None
    bbands_middle: Optional[float] = None
    bbands_lower: Optional[float] = None

class TechnicalIndicatorsResponse(BaseModel):
    ticker: str
    indicators: List[TechnicalIndicatorRecord]

class NewsArticleSchema(BaseModel):
    id: Optional[int] = None
    ticker: str
    headline: str
    description: Optional[str] = None
    source: Optional[str] = None
    published_at: str
    url: Optional[str] = None
    sentiment: Optional[str] = None
    sentiment_score: Optional[float] = None

class DailySentimentPoint(BaseModel):
    date: str
    sentiment_score: float
    article_count: int
    positive_count: int
    neutral_count: int
    negative_count: int

class SentimentSummaryResponse(BaseModel):
    ticker: str
    total_articles: int
    positive_count: int
    neutral_count: int
    negative_count: int
    positive_pct: float
    neutral_pct: float
    negative_pct: float
    average_score: float
    daily_sentiment: List[DailySentimentPoint]
    articles: List[NewsArticleSchema]

class ActualVsPredictedPoint(BaseModel):
    date: str
    actual: Optional[float] = None
    predicted: float

class ModelMetricsResponse(BaseModel):
    mae: float
    rmse: float
    mape: float
    lookback_window: int = 60
    model_architecture: str = "2-Layer LSTM (64-64) + Dropout(0.2) + Dense(32) + Linear(1)"
    features_count: int = 12

class PredictionResponse(BaseModel):
    ticker: str
    company_name: str
    current_price: float
    predicted_price: float
    predicted_change: float
    predicted_change_percent: float
    prediction_horizon: str = "Next Trading Day"
    signal: str   # Bullish, Bearish, Neutral
    currency: str = "USD"
    metrics: ModelMetricsResponse
    actual_vs_predicted: List[ActualVsPredictedPoint]
