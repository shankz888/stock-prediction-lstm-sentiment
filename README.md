# Stock Price Prediction Using LSTM with News Sentiment Analysis

An end-to-end financial analytics and machine-learning platform that combines **historical stock-market data (OHLCV)**, **technical indicators**, and **financial news sentiment** (analyzed via **FinBERT**) to predict the **next trading day's closing price** using a **2-layer LSTM deep-learning neural network**.

Built according to the Master Product Requirements Document (PRD).

---

## 1. System Architecture

```text
                  USER
                   │
                   ▼
             Search Stock (e.g. AAPL, RELIANCE, TSLA)
                   │
        ┌──────────┴──────────┐
        ▼                     ▼
   Stock Market API        News API / Feeds
        │                     │
 Historical OHLCV       Financial News
        │                     │
Technical Indicators       FinBERT NLP
 (SMA, EMA, RSI,        (Positive, Neutral,
  MACD, BBands, Vol)     Negative Classifications)
        │                     │
        │               Daily Sentiment Score
        │                     │
        └──────────┬──────────┘
                   ▼
       12-Feature Dataset Matrix
                   ▼
        MinMaxScaler Normalization
                   ▼
          60-Day Lookback Sequences
                   ▼
          2-Layer LSTM Model
                   ▼
       Next-Day Closing Prediction
                   ▼
            FastAPI Backend
                   ▼
            React Dashboard
       ┌───────────┼───────────┐
       ▼           ▼           ▼
  Prediction     Charts     News &
  Card & Metrics (Actual/   Sentiment
                 Predicted)
```

---

## 2. Key Features

### Stock Search & Real-Time Quotes
- Supports both US equities (`AAPL`, `TSLA`, `NVDA`, `MSFT`, etc.) and Indian NSE equities (`RELIANCE.NS`, `TCS.NS`, `INFY.NS`).
- Displays Company Name, Ticker, Current Price, Daily Change, Daily % Change, Volume, Day Range.

### Technical Feature Engineering
Calculates 5 technical indicators directly from historical OHLCV data:
1. **SMA**: Simple Moving Average (20-day, 50-day)
2. **EMA**: Exponential Moving Average (12-day, 26-day, 20-day)
3. **RSI**: Relative Strength Index (14-day momentum oscillator)
4. **MACD**: Moving Average Convergence Divergence (12 EMA - 26 EMA), 9 EMA Signal, Histogram
5. **Bollinger Bands**: 20-day SMA, Upper (+2σ), Lower (-2σ)
6. **Volume**: Market liquidity feature

### Financial News & FinBERT Sentiment Analysis
- Mandatory News API integration with fallback to live financial feeds.
- Automatic relevance filtering and title deduplication.
- FinBERT model (`ProsusAI/finbert`) classifies each article into **Positive**, **Neutral**, or **Negative** with confidence scores.
- Article sentiment is aggregated into a daily numerical score (`[-1.0, +1.0]`) aligned with trading days.

### LSTM Time-Series Deep Learning
- **Lookback Window**: 60 trading days (`[Samples × 60 × 12]`).
- **Architecture**:
  - Input Layer (`batch_size`, `60`, `12`)
  - LSTM Layer 1 (64 hidden units, return sequences)
  - Dropout (0.2)
  - LSTM Layer 2 (64 hidden units)
  - Dropout (0.2)
  - Dense Layer (32 hidden units, ReLU)
  - Output Linear Layer (1 unit, predicting next day Close)
- **Target**: Next Trading Day Closing Price + Predicted % Change + Directional Signal (Bullish/Bearish/Neutral).
- **Evaluation Metrics**:
  - **MAE** (Mean Absolute Error)
  - **RMSE** (Root Mean Squared Error)
  - **MAPE** (Mean Absolute Percentage Error %)

### Interactive Dashboard
- Modern, dark-themed responsive interface built with React, Vite, Tailwind CSS, Lucide Icons, and Recharts.
- Interactive Actual vs Predicted price line chart.
- Technical Indicator tabs (SMA/EMA, Bollinger Bands, RSI, MACD, Volume).
- News Sentiment Analytics (article counts, sentiment distribution, daily trend).
- News feed with external "Read More" links and sentiment badges.

---

## 3. Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | React 18, Vite, Tailwind CSS, Recharts, Lucide Icons |
| **Backend** | Python FastAPI, Uvicorn, Pydantic, SQLAlchemy |
| **Deep Learning** | PyTorch (LSTM), MPS / CUDA / CPU acceleration |
| **NLP** | Hugging Face Transformers (`ProsusAI/finbert`) |
| **Stock Data** | Alpha Vantage & Yahoo Finance (`yfinance`) |
| **News** | NewsAPI & Live Financial Feeds |
| **Database** | SQLite (zero-config local cache, configurable to PostgreSQL) |

---

## 4. Quick Start

### Prerequisites
- Python 3.10+ (or Python 3.12/3.13)
- Node.js 18+ and npm

### One-Click Launch
Run the provided launcher script:
```bash
./start.sh
```

This will automatically:
1. Set up the Python virtual environment and dependencies.
2. Launch the FastAPI backend on `http://localhost:8000`.
3. Launch the React frontend on `http://localhost:5173`.

---

## 5. Manual Setup

### 1. Backend Setup
```bash
# From project root
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt

# Start backend server
PYTHONPATH=. python -m uvicorn backend.app.main:app --reload --port 8000
```

### 2. Frontend Setup
```bash
# In another terminal window
cd frontend
npm install
npm run dev
```

Visit `http://localhost:5173` in your browser.

---

## 6. API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/stock/{ticker}` | Current stock quote & info |
| `GET` | `/stock/{ticker}/history` | Historical OHLCV dataset |
| `GET` | `/stock/{ticker}/indicators` | Calculated technical indicators |
| `GET` | `/news/{ticker}` | Filtered & deduplicated news articles |
| `GET` | `/news/{ticker}/sentiment` | Sentiment classifications & daily aggregate |
| `GET` | `/predict/{ticker}` | End-to-end LSTM prediction & metrics |
| `GET` | `/model/metrics` | Model performance (MAE, RMSE, MAPE) |
| `GET` | `/docs` | Interactive Swagger API documentation |

---

## 7. Running Tests

Run the unit test suite:
```bash
PYTHONPATH=. ./venv/bin/python backend/tests/test_pipeline.py
PYTHONPATH=. ./venv/bin/python backend/tests/test_api_endpoints.py
```

---

## 8. Disclaimer

This application is developed strictly for **educational and analytical purposes**. The stock price predictions produced by the machine learning model are statistical estimates and do not guarantee future prices. They do not constitute financial advice.
