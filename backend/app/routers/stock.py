from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from backend.app.database import get_db
from backend.app.schemas.stock import (
    StockQuote,
    HistoricalDataResponse,
    TechnicalIndicatorsResponse,
    TechnicalIndicatorRecord
)
from backend.app.services.stock_service import (
    get_stock_quote,
    get_historical_stock_data,
    resolve_ticker
)
from backend.app.services.technical_indicators import add_technical_indicators

router = APIRouter(prefix="/stock", tags=["Stock Data"])

@router.get("/{ticker}", response_model=StockQuote)
def get_quote_endpoint(ticker: str):
    """
    Get current stock information (PRD Section 7 & 33).
    Returns company name, ticker, current price, daily change, %, and volume.
    """
    quote = get_stock_quote(ticker)
    return quote

@router.get("/{ticker}/history", response_model=HistoricalDataResponse)
def get_history_endpoint(
    ticker: str,
    period: str = Query("2y", description="Time period: 1mo, 3mo, 6mo, 1y, 2y, 5y"),
    db: Session = Depends(get_db)
):
    """
    Get historical OHLCV data (PRD Section 8 & 33).
    """
    resolved = resolve_ticker(ticker)
    df = get_historical_stock_data(resolved, period=period, db=db)
    if df.empty:
        raise HTTPException(status_code=404, detail=f"No historical data found for {ticker}")

    records = df.to_dict(orient="records")
    return {
        "ticker": resolved,
        "total_records": len(records),
        "data": records
    }

@router.get("/{ticker}/indicators", response_model=TechnicalIndicatorsResponse)
def get_indicators_endpoint(
    ticker: str,
    period: str = Query("1y", description="Time period"),
    db: Session = Depends(get_db)
):
    """
    Calculate and return technical indicators: SMA, EMA, RSI, MACD, Bollinger Bands (PRD Section 9 & 33).
    """
    resolved = resolve_ticker(ticker)
    df = get_historical_stock_data(resolved, period=period, db=db)
    if df.empty:
        raise HTTPException(status_code=404, detail=f"No data available for indicator computation on {ticker}")

    df_ind = add_technical_indicators(df)
    records = []
    for _, row in df_ind.iterrows():
        records.append(TechnicalIndicatorRecord(
            date=row["date"],
            close=round(float(row["close"]), 2),
            volume=float(row["volume"]),
            sma_20=round(float(row["sma_20"]), 2) if not row.isna()["sma_20"] else None,
            sma_50=round(float(row["sma_50"]), 2) if not row.isna()["sma_50"] else None,
            ema_12=round(float(row["ema_12"]), 2) if not row.isna()["ema_12"] else None,
            ema_20=round(float(row["ema_20"]), 2) if not row.isna()["ema_20"] else None,
            ema_26=round(float(row["ema_26"]), 2) if not row.isna()["ema_26"] else None,
            rsi=round(float(row["rsi"]), 2) if not row.isna()["rsi"] else None,
            macd=round(float(row["macd"]), 2) if not row.isna()["macd"] else None,
            macd_signal=round(float(row["macd_signal"]), 2) if not row.isna()["macd_signal"] else None,
            macd_hist=round(float(row["macd_hist"]), 2) if not row.isna()["macd_hist"] else None,
            bbands_upper=round(float(row["bbands_upper"]), 2) if not row.isna()["bbands_upper"] else None,
            bbands_middle=round(float(row["bbands_middle"]), 2) if not row.isna()["bbands_middle"] else None,
            bbands_lower=round(float(row["bbands_lower"]), 2) if not row.isna()["bbands_lower"] else None,
        ))

    return {
        "ticker": resolved,
        "indicators": records
    }
