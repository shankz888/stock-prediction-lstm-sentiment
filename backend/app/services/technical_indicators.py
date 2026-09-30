import pandas as pd
import numpy as np

def calculate_sma(series: pd.Series, period: int) -> pd.Series:
    """Calculate Simple Moving Average."""
    return series.rolling(window=period, min_periods=1).mean()

def calculate_ema(series: pd.Series, period: int) -> pd.Series:
    """Calculate Exponential Moving Average."""
    return series.ewm(span=period, adjust=False, min_periods=1).mean()

def calculate_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """
    Calculate Relative Strength Index (RSI).
    Standard formula with exponential smoothing.
    """
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    # Use wilder's exponential smoothing or standard ewm
    avg_gain = gain.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/period, min_periods=period, adjust=False).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    # Fill initial NaNs with neutral 50.0
    return rsi.fillna(50.0)

def calculate_macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
    """
    Calculate MACD Line, Signal Line, and MACD Histogram.
    """
    ema_fast = calculate_ema(series, fast)
    ema_slow = calculate_ema(series, slow)
    macd_line = ema_fast - ema_slow
    signal_line = calculate_ema(macd_line, signal)
    macd_hist = macd_line - signal_line
    return macd_line, signal_line, macd_hist

def calculate_bollinger_bands(series: pd.Series, period: int = 20, num_std: float = 2.0):
    """
    Calculate Bollinger Bands (Middle, Upper, Lower).
    """
    middle = calculate_sma(series, period)
    rolling_std = series.rolling(window=period, min_periods=1).std().fillna(0)
    upper = middle + (rolling_std * num_std)
    lower = middle - (rolling_std * num_std)
    return upper, middle, lower

def add_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add SMA, EMA, RSI, MACD, and Bollinger Bands to an OHLCV DataFrame.
    Expects df columns: ['open', 'high', 'low', 'close', 'volume'].
    """
    df = df.copy()
    close = df['close']

    # SMAs
    df['sma_20'] = calculate_sma(close, 20)
    df['sma_50'] = calculate_sma(close, 50)

    # EMAs
    df['ema_12'] = calculate_ema(close, 12)
    df['ema_20'] = calculate_ema(close, 20)
    df['ema_26'] = calculate_ema(close, 26)

    # RSI
    df['rsi'] = calculate_rsi(close, 14)

    # MACD
    macd, signal, hist = calculate_macd(close, fast=12, slow=26, signal=9)
    df['macd'] = macd
    df['macd_signal'] = signal
    df['macd_hist'] = hist

    # Bollinger Bands
    upper, middle, lower = calculate_bollinger_bands(close, period=20, num_std=2.0)
    df['bbands_upper'] = upper
    df['bbands_middle'] = middle
    df['bbands_lower'] = lower

    return df
