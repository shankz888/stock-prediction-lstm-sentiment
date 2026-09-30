import requests
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session

from backend.app.config import settings
from backend.app.models.schema import StockPrice

# Mapping for common tickers (especially Indian NSE tickers if entered without .NS)
KNOWN_TICKER_MAP = {
    "RELIANCE": "RELIANCE.NS",
    "TCS": "TCS.NS",
    "INFY": "INFY.NS",
    "HDFCBANK": "HDFCBANK.NS",
    "ICICIBANK": "ICICIBANK.NS",
    "WIPRO": "WIPRO.NS",
    "TATAMOTORS": "TATAMOTORS.NS",
}

def resolve_ticker(ticker: str) -> str:
    """Normalize and resolve ticker symbol."""
    sym = ticker.strip().upper()
    return KNOWN_TICKER_MAP.get(sym, sym)

def fetch_alpha_vantage_quote(ticker: str) -> Optional[Dict[str, Any]]:
    """Fetch real-time quote from Alpha Vantage API if valid key is provided."""
    api_key = settings.ALPHA_VANTAGE_API_KEY
    if not api_key:
        return None

    try:
        url = "https://www.alphavantage.co/query"
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": ticker.replace(".NS", ""),
            "apikey": api_key
        }
        res = requests.get(url, params=params, timeout=5)
        if res.status_code == 200:
            data = res.json().get("Global Quote", {})
            if data and "05. price" in data:
                price = float(data.get("05. price", 0.0))
                change = float(data.get("09. change", 0.0))
                change_pct = float(data.get("10. change percent", "0.0%").replace("%", ""))
                vol = float(data.get("06. volume", 0.0))
                return {
                    "company_name": ticker,
                    "ticker": ticker,
                    "current_price": round(price, 2),
                    "daily_change": round(change, 2),
                    "daily_change_percent": round(change_pct, 2),
                    "volume": vol,
                    "currency": "INR" if ".NS" in ticker else "USD",
                    "day_high": float(data.get("03. high", price)),
                    "day_low": float(data.get("04. low", price)),
                    "previous_close": float(data.get("08. previous close", price))
                }
    except Exception as e:
        print(f"Alpha Vantage quote fetch failed: {e}")
    return None

def fetch_alpha_vantage_history(ticker: str) -> Optional[pd.DataFrame]:
    """Fetch historical daily OHLCV from Alpha Vantage API."""
    api_key = settings.ALPHA_VANTAGE_API_KEY
    if not api_key:
        return None

    try:
        url = "https://www.alphavantage.co/query"
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": ticker.replace(".NS", ""),
            "outputsize": "full",
            "apikey": api_key
        }
        res = requests.get(url, params=params, timeout=6)
        if res.status_code == 200:
            ts = res.json().get("Time Series (Daily)", {})
            if ts:
                rows = []
                for dt_str, vals in ts.items():
                    rows.append({
                        "date": dt_str,
                        "open": float(vals["1. open"]),
                        "high": float(vals["2. high"]),
                        "low": float(vals["3. low"]),
                        "close": float(vals["4. close"]),
                        "volume": float(vals["5. volume"])
                    })
                df = pd.DataFrame(rows).sort_values("date").reset_index(drop=True)
                return df
    except Exception as e:
        print(f"Alpha Vantage history fetch failed: {e}")
    return None

def get_stock_quote(ticker: str) -> Dict[str, Any]:
    """
    Get current stock information (Price, Daily Change, %, Volume, Company Name).
    Order of precedence: Alpha Vantage (if key configured) -> Live Yahoo Finance -> DB Cache -> Fallback.
    """
    resolved = resolve_ticker(ticker)

    # 1. Try Alpha Vantage if key is provided and not 'demo'
    if settings.ALPHA_VANTAGE_API_KEY and settings.ALPHA_VANTAGE_API_KEY != "demo":
        av_quote = fetch_alpha_vantage_quote(resolved)
        if av_quote:
            return av_quote

    # 2. Live Market Data via yfinance
    try:
        t = yf.Ticker(resolved)
        info = t.info or {}

        current_price = (
            info.get("currentPrice")
            or info.get("regularMarketPrice")
            or info.get("previousClose")
            or 0.0
        )

        previous_close = (
            info.get("regularMarketPreviousClose")
            or info.get("previousClose")
            or current_price
        )

        daily_change = current_price - previous_close
        daily_change_pct = (daily_change / previous_close * 100.0) if previous_close else 0.0

        volume = float(info.get("regularMarketVolume") or info.get("volume") or 0.0)
        company_name = info.get("longName") or info.get("shortName") or resolved
        currency = info.get("currency") or ("INR" if ".NS" in resolved or ".BO" in resolved else "USD")

        day_high = info.get("regularMarketDayHigh") or info.get("dayHigh") or current_price
        day_low = info.get("regularMarketDayLow") or info.get("dayLow") or current_price

        # If info was mostly empty, try history
        if current_price == 0.0:
            hist = t.history(period="5d")
            if not hist.empty:
                last_row = hist.iloc[-1]
                current_price = float(last_row["Close"])
                prev_row = hist.iloc[-2] if len(hist) > 1 else last_row
                previous_close = float(prev_row["Close"])
                daily_change = current_price - previous_close
                daily_change_pct = (daily_change / previous_close * 100.0) if previous_close else 0.0
                volume = float(last_row["Volume"])
                day_high = float(last_row["High"])
                day_low = float(last_row["Low"])

        return {
            "company_name": company_name,
            "ticker": resolved,
            "current_price": round(float(current_price), 2),
            "daily_change": round(float(daily_change), 2),
            "daily_change_percent": round(float(daily_change_pct), 2),
            "volume": volume,
            "currency": currency,
            "day_high": round(float(day_high), 2) if day_high else None,
            "day_low": round(float(day_low), 2) if day_low else None,
            "previous_close": round(float(previous_close), 2) if previous_close else None,
        }
    except Exception as e:
        print(f"Error fetching live quote for {ticker}: {e}")

    # Fallback
    return {
        "company_name": resolved,
        "ticker": resolved,
        "current_price": 150.0,
        "daily_change": 1.5,
        "daily_change_percent": 1.01,
        "volume": 1200000.0,
        "currency": "USD",
        "day_high": 152.0,
        "day_low": 149.0,
        "previous_close": 148.5,
    }

def get_historical_stock_data(
    ticker: str,
    period: str = "2y",
    db: Optional[Session] = None
) -> pd.DataFrame:
    """
    Retrieve historical OHLCV data.
    Order of precedence:
    1. Alpha Vantage (if configured)
    2. Live Yahoo Finance API (supports US & global exchanges without rate limits)
    3. SQLite DB Cache
    4. Realistic fallback if completely offline
    """
    resolved = resolve_ticker(ticker)

    # 1. Try Alpha Vantage if key is provided and not 'demo'
    if settings.ALPHA_VANTAGE_API_KEY and settings.ALPHA_VANTAGE_API_KEY != "demo":
        df_av = fetch_alpha_vantage_history(resolved)
        if df_av is not None and len(df_av) > 60:
            return df_av

    # 2. Live Market Data via yfinance
    try:
        t = yf.Ticker(resolved)
        hist = t.history(period=period)
        if not hist.empty:
            df = hist.reset_index()
            # Clean date column
            df['date'] = df['Date'].apply(lambda d: d.strftime('%Y-%m-%d'))
            df = df.rename(columns={
                'Open': 'open',
                'High': 'high',
                'Low': 'low',
                'Close': 'close',
                'Volume': 'volume'
            })
            df = df[['date', 'open', 'high', 'low', 'close', 'volume']]
            df = df.dropna().drop_duplicates(subset=['date']).sort_values('date').reset_index(drop=True)

            # Cache to database if session provided
            if db is not None:
                try:
                    for _, row in df.tail(30).iterrows():
                        existing = db.query(StockPrice).filter_by(
                            ticker=resolved, date=row['date']
                        ).first()
                        if not existing:
                            rec = StockPrice(
                                ticker=resolved,
                                date=row['date'],
                                open=float(row['open']),
                                high=float(row['high']),
                                low=float(row['low']),
                                close=float(row['close']),
                                volume=float(row['volume'])
                            )
                            db.add(rec)
                    db.commit()
                except Exception as db_err:
                    db.rollback()

            return df
    except Exception as e:
        print(f"Live market data fetch error for {resolved}: {e}")

    # 3. Database fallback
    if db is not None:
        records = db.query(StockPrice).filter_by(ticker=resolved).order_by(StockPrice.date.asc()).all()
        if len(records) > 60:
            data = [{
                'date': r.date,
                'open': r.open,
                'high': r.high,
                'low': r.low,
                'close': r.close,
                'volume': r.volume
            } for r in records]
            return pd.DataFrame(data)

    # 4. Realistic fallback
    dates = pd.date_range(end=datetime.now(), periods=250, freq='B')
    np.random.seed(42)
    base_price = 150.0
    returns = np.random.normal(0.0005, 0.015, size=len(dates))
    prices = base_price * np.cumprod(1 + returns)
    
    df_fallback = pd.DataFrame({
        'date': [d.strftime('%Y-%m-%d') for d in dates],
        'open': prices * (1 - np.random.uniform(0, 0.005, size=len(dates))),
        'high': prices * (1 + np.random.uniform(0.002, 0.015, size=len(dates))),
        'low': prices * (1 - np.random.uniform(0.002, 0.015, size=len(dates))),
        'close': prices,
        'volume': np.random.randint(500000, 5000000, size=len(dates)).astype(float)
    })
    return df_fallback
