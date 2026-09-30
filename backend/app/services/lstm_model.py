import os
import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader
import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from backend.app.config import settings
from backend.app.models.schema import Prediction

# Device configuration (MPS for Apple Silicon, CUDA for Nvidia, CPU fallback)
def get_device():
    if torch.backends.mps.is_available():
        return torch.device("mps")
    elif torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")

class StockLSTM(nn.Module):
    """
    2-Layer LSTM with Dropout and Dense layers conforming to PRD Section 21.
    Input shape: (batch_size, seq_len, num_features)
    """
    def __init__(self, input_dim: int = 12, hidden_dim: int = 64, dropout: float = 0.2):
        super(StockLSTM, self).__init__()
        self.lstm = nn.LSTM(
            input_size=input_dim,
            hidden_size=hidden_dim,
            num_layers=2,
            batch_first=True,
            dropout=dropout
        )
        self.fc1 = nn.Linear(hidden_dim, 32)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(dropout)
        self.fc2 = nn.Linear(32, 1)

    def forward(self, x):
        # x: (batch_size, seq_len, input_dim)
        lstm_out, _ = self.lstm(x)
        # Take the output of the last time step
        last_time_step = lstm_out[:, -1, :]
        dense_out = self.fc1(last_time_step)
        dense_out = self.relu(dense_out)
        dense_out = self.dropout(dense_out)
        out = self.fc2(dense_out)
        return out

def train_and_evaluate_lstm(
    prepared_data: Dict[str, Any],
    epochs: int = 25,
    batch_size: int = 16,
    lr: float = 0.001
) -> Dict[str, Any]:
    """
    Trains the LSTM model on training sequences and evaluates on the unseen test set.
    Calculates MAE, RMSE, MAPE, and generates predictions.
    """
    device = get_device()
    X_train = prepared_data["X_train"]
    y_train = prepared_data["y_train"]
    X_test = prepared_data["X_test"]
    y_test = prepared_data["y_test"]
    target_scaler = prepared_data["target_scaler"]
    test_dates = prepared_data["test_dates"]
    latest_seq = prepared_data["latest_sequence"]

    input_dim = X_train.shape[2]
    model = StockLSTM(input_dim=input_dim, hidden_dim=64, dropout=0.2).to(device)
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)

    # Prepare PyTorch DataLoaders
    train_dataset = TensorDataset(
        torch.tensor(X_train, dtype=torch.float32),
        torch.tensor(y_train, dtype=torch.float32)
    )
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=False)

    # Training Loop
    model.train()
    for epoch in range(epochs):
        for batch_X, batch_y in train_loader:
            batch_X, batch_y = batch_X.to(device), batch_y.to(device)
            optimizer.zero_grad()
            preds = model(batch_X)
            loss = criterion(preds, batch_y)
            loss.backward()
            optimizer.step()

    # Evaluation on Test Data
    model.eval()
    with torch.no_grad():
        test_inputs = torch.tensor(X_test, dtype=torch.float32).to(device)
        test_preds_scaled = model(test_inputs).cpu().numpy()

    # Invert scaling to real price figures
    actual_prices = target_scaler.inverse_transform(y_test).flatten()
    pred_prices = target_scaler.inverse_transform(test_preds_scaled).flatten()

    # Calculate Evaluation Metrics (PRD Section 25)
    mae = float(np.mean(np.abs(actual_prices - pred_prices)))
    rmse = float(np.sqrt(np.mean((actual_prices - pred_prices) ** 2)))
    # Avoid zero division in MAPE
    non_zero = actual_prices != 0
    mape = float(np.mean(np.abs((actual_prices[non_zero] - pred_prices[non_zero]) / actual_prices[non_zero])) * 100.0)

    # Next Trading Day Prediction (PRD Section 22)
    with torch.no_grad():
        next_input = torch.tensor(latest_seq, dtype=torch.float32).to(device)
        next_pred_scaled = model(next_input).cpu().numpy()
        next_day_predicted_price = float(target_scaler.inverse_transform(next_pred_scaled)[0, 0])

    # Build Actual vs Predicted series for visualization
    actual_vs_predicted = []
    for dt, act, prd in zip(test_dates, actual_prices, pred_prices):
        actual_vs_predicted.append({
            "date": dt,
            "actual": round(float(act), 2),
            "predicted": round(float(prd), 2)
        })

    # Forecast next trading date (skipping weekend)
    last_dt = datetime.strptime(test_dates[-1], "%Y-%m-%d")
    next_trading_day = last_dt + timedelta(days=1)
    if next_trading_day.weekday() == 5:  # Saturday -> Monday
        next_trading_day += timedelta(days=2)
    elif next_trading_day.weekday() == 6:  # Sunday -> Monday
        next_trading_day += timedelta(days=1)
    next_date_str = next_trading_day.strftime("%Y-%m-%d")

    actual_vs_predicted.append({
        "date": next_date_str,
        "actual": None,
        "predicted": round(next_day_predicted_price, 2)
    })

    return {
        "model": model,
        "mae": round(mae, 2),
        "rmse": round(rmse, 2),
        "mape": round(mape, 2),
        "predicted_next_close": round(next_day_predicted_price, 2),
        "next_date": next_date_str,
        "actual_vs_predicted": actual_vs_predicted
    }

def run_lstm_prediction_pipeline(
    ticker: str,
    df_ohlcv,
    articles: List[Dict[str, Any]],
    current_price: float,
    company_name: str,
    db: Optional[Session] = None
) -> Dict[str, Any]:
    """
    Executes the full end-to-end LSTM + Sentiment prediction pipeline.
    """
    from backend.app.services.feature_pipeline import (
        build_combined_feature_matrix,
        prepare_lstm_sequences
    )

    # 1. Feature Engineering
    df_features = build_combined_feature_matrix(df_ohlcv, articles)

    # 2. Sequence Preparation
    prepared = prepare_lstm_sequences(
        df_features,
        lookback_window=settings.LOOKBACK_WINDOW,
        train_split=0.8
    )

    # 3. Model Training & Evaluation
    results = train_and_evaluate_lstm(
        prepared,
        epochs=settings.LSTM_EPOCHS,
        batch_size=settings.LSTM_BATCH_SIZE
    )

    predicted_price = results["predicted_next_close"]
    predicted_change = predicted_price - current_price
    predicted_change_pct = (predicted_change / current_price * 100.0) if current_price else 0.0

    # Determine Signal
    if predicted_change_pct > 0.3:
        signal = "Bullish"
    elif predicted_change_pct < -0.3:
        signal = "Bearish"
    else:
        signal = "Neutral"

    # Persist prediction to database
    if db is not None:
        try:
            pred_record = Prediction(
                ticker=ticker,
                prediction_date=results["next_date"],
                actual_price=None,
                predicted_price=predicted_price,
                model_version="lstm_v1_finbert",
                mae=results["mae"],
                rmse=results["rmse"],
                mape=results["mape"]
            )
            db.add(pred_record)
            db.commit()
        except Exception as e:
            db.rollback()

    return {
        "ticker": ticker,
        "company_name": company_name,
        "current_price": round(current_price, 2),
        "predicted_price": round(predicted_price, 2),
        "predicted_change": round(predicted_change, 2),
        "predicted_change_percent": round(predicted_change_pct, 2),
        "prediction_horizon": "Next Trading Day",
        "signal": signal,
        "currency": "INR" if ".NS" in ticker or ".BO" in ticker else "USD",
        "metrics": {
            "mae": results["mae"],
            "rmse": results["rmse"],
            "mape": results["mape"],
            "lookback_window": settings.LOOKBACK_WINDOW,
            "model_architecture": "2-Layer LSTM (64-64) + Dropout(0.2) + Dense(32) + Linear(1)",
            "features_count": 12
        },
        "actual_vs_predicted": results["actual_vs_predicted"]
    }
