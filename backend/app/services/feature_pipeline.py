import numpy as np
import pandas as pd
from typing import Tuple, List, Dict, Any, Optional
from sklearn.preprocessing import MinMaxScaler

from backend.app.services.technical_indicators import add_technical_indicators
from backend.app.services.sentiment_service import aggregate_daily_sentiment

# Ordered list of 12 features as specified in PRD Section 16 & 20
FEATURE_COLUMNS = [
    "open",
    "high",
    "low",
    "close",
    "volume",
    "sma_20",
    "ema_20",
    "rsi",
    "macd",
    "bbands_upper",
    "bbands_lower",
    "sentiment_score"
]

def build_combined_feature_matrix(
    df_ohlcv: pd.DataFrame,
    articles: List[Dict[str, Any]]
) -> pd.DataFrame:
    """
    Combines:
    1. Historical OHLCV
    2. Technical Indicators (SMA, EMA, RSI, MACD, Bollinger Bands)
    3. Daily Aggregated News Sentiment aligned with trading dates.
    """
    # 1. Calculate technical indicators
    df_ind = add_technical_indicators(df_ohlcv)

    # 2. Compute daily news sentiment
    daily_sent = aggregate_daily_sentiment(articles)

    # 3. Align sentiment with trading dates (neutral 0.0 when no news)
    df_ind["sentiment_score"] = df_ind["date"].apply(
        lambda dt: daily_sent[dt]["sentiment_score"] if dt in daily_sent else 0.0
    )

    # Clean any remaining NaNs
    df_clean = df_ind.ffill().bfill().copy()

    # Ensure all required feature columns exist
    for col in FEATURE_COLUMNS:
        if col not in df_clean.columns:
            df_clean[col] = 0.0

    return df_clean

def prepare_lstm_sequences(
    df_features: pd.DataFrame,
    lookback_window: int = 60,
    train_split: float = 0.8
) -> Dict[str, Any]:
    """
    Normalizes features, creates 60-day sliding window sequences,
    and splits chronologically into Train and Test sets.

    Returns:
    {
        "X_train": np.ndarray (shape: [N_train, lookback_window, 12]),
        "y_train": np.ndarray (shape: [N_train, 1]),
        "X_test": np.ndarray (shape: [N_test, lookback_window, 12]),
        "y_test": np.ndarray (shape: [N_test, 1]),
        "test_dates": List[str],
        "feature_scaler": MinMaxScaler,
        "target_scaler": MinMaxScaler,
        "latest_sequence": np.ndarray (shape: [1, lookback_window, 12]),
        "df_clean": pd.DataFrame
    }
    """
    feature_matrix = df_features[FEATURE_COLUMNS].values
    target_values = df_features[["close"]].values
    dates = df_features["date"].tolist()

    total_len = len(df_features)
    if total_len <= lookback_window + 10:
        raise ValueError(
            f"Not enough data points ({total_len}) for lookback window of {lookback_window}. "
            f"At least {lookback_window + 15} trading days are required."
        )

    # Determine chronological split point
    train_size = int(total_len * train_split)
    # Ensure train_size leaves at least some samples for test
    if train_size <= lookback_window:
        train_size = lookback_window + 5

    # Fit scalers strictly on training data
    feature_scaler = MinMaxScaler(feature_range=(0, 1))
    feature_scaler.fit(feature_matrix[:train_size])

    target_scaler = MinMaxScaler(feature_range=(0, 1))
    target_scaler.fit(target_values[:train_size])

    # Transform all data using fitted scalers
    scaled_features = feature_scaler.transform(feature_matrix)
    scaled_targets = target_scaler.transform(target_values)

    # Generate sequences [Samples, lookback_window, Features]
    X, y, seq_dates = [], [], []
    for i in range(lookback_window, total_len):
        X.append(scaled_features[i - lookback_window:i])
        y.append(scaled_targets[i, 0])
        seq_dates.append(dates[i])

    X = np.array(X, dtype=np.float32)
    y = np.array(y, dtype=np.float32).reshape(-1, 1)

    # Split into train and test sets chronologically
    split_idx = max(train_size - lookback_window, 1)
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]
    test_dates = seq_dates[split_idx:]

    # Sequence for forecasting the next trading day (last 60 days of features)
    latest_sequence = scaled_features[-lookback_window:][np.newaxis, :, :]

    return {
        "X_train": X_train,
        "y_train": y_train,
        "X_test": X_test,
        "y_test": y_test,
        "test_dates": test_dates,
        "feature_scaler": feature_scaler,
        "target_scaler": target_scaler,
        "latest_sequence": latest_sequence.astype(np.float32),
        "df_clean": df_features
    }
