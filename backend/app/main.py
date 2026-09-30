from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backend.app.config import settings
from backend.app.database import init_db
from backend.app.routers import stock, news, prediction

# Initialize DB tables immediately
init_db()

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(
    title="Stock Price Prediction Using LSTM with News Sentiment Analysis",
    description="Educational and analytical system combining OHLCV, Technical Indicators, FinBERT sentiment, and 2-layer LSTM deep learning.",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS for React/Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routers
app.include_router(stock.router)
app.include_router(news.router)
app.include_router(prediction.router)

@app.get("/")
def root():
    return {
        "status": "online",
        "service": "Stock Price Prediction Using LSTM with News Sentiment Analysis",
        "endpoints": {
            "quote": "/stock/{ticker}",
            "history": "/stock/{ticker}/history",
            "indicators": "/stock/{ticker}/indicators",
            "news": "/news/{ticker}",
            "sentiment": "/news/{ticker}/sentiment",
            "prediction": "/predict/{ticker}",
            "metrics": "/model/metrics",
            "docs": "/docs"
        }
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}
