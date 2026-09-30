from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from backend.app.database import get_db
from backend.app.schemas.stock import NewsArticleSchema, SentimentSummaryResponse
from backend.app.services.stock_service import resolve_ticker, get_stock_quote
from backend.app.services.news_service import get_recent_news
from backend.app.services.sentiment_service import (
    process_and_score_news,
    get_sentiment_overview
)

router = APIRouter(prefix="/news", tags=["Financial News & Sentiment"])

@router.get("/{ticker}", response_model=List[NewsArticleSchema])
def get_news_endpoint(
    ticker: str,
    limit: int = Query(25, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    Get recent company financial news (PRD Section 11 & 33).
    """
    resolved = resolve_ticker(ticker)
    quote = get_stock_quote(resolved)
    raw_articles = get_recent_news(
        resolved,
        company_name=quote.get("company_name"),
        limit=limit,
        db=db
    )
    processed = process_and_score_news(raw_articles, db=db)
    return processed

@router.get("/{ticker}/sentiment", response_model=SentimentSummaryResponse)
def get_news_sentiment_endpoint(
    ticker: str,
    limit: int = Query(30, ge=1, le=60),
    db: Session = Depends(get_db)
):
    """
    Get financial news sentiment results and daily aggregation (PRD Section 14, 15, 28 & 33).
    """
    resolved = resolve_ticker(ticker)
    quote = get_stock_quote(resolved)
    raw_articles = get_recent_news(
        resolved,
        company_name=quote.get("company_name"),
        limit=limit,
        db=db
    )
    processed = process_and_score_news(raw_articles, db=db)
    overview = get_sentiment_overview(resolved, processed)
    return overview
