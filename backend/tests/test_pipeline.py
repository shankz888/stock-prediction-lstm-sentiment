import unittest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

from backend.app.services.technical_indicators import (
    calculate_sma,
    calculate_ema,
    calculate_rsi,
    calculate_macd,
    calculate_bollinger_bands,
    add_technical_indicators
)
from backend.app.services.sentiment_service import (
    analyze_sentiment_lexicon,
    aggregate_daily_sentiment,
    get_sentiment_overview
)
from backend.app.services.feature_pipeline import (
    FEATURE_COLUMNS,
    build_combined_feature_matrix,
    prepare_lstm_sequences
)
from backend.app.services.lstm_model import (
    StockLSTM,
    train_and_evaluate_lstm
)

class TestStockPredictionPipeline(unittest.TestCase):

    def setUp(self):
        # Generate synthetic realistic OHLCV dataset of 120 days
        np.random.seed(42)
        n = 120
        dates = pd.date_range(end=datetime.now(), periods=n, freq='B')
        base_price = 100.0
        returns = np.random.normal(0.001, 0.015, size=n)
        prices = base_price * np.cumprod(1 + returns)

        self.df_ohlcv = pd.DataFrame({
            'date': [d.strftime('%Y-%m-%d') for d in dates],
            'open': prices * 0.99,
            'high': prices * 1.02,
            'low': prices * 0.98,
            'close': prices,
            'volume': np.random.randint(100000, 1000000, size=n).astype(float)
        })

        self.sample_articles = [
            {
                "ticker": "AAPL",
                "headline": "Apple reports record revenue growth and positive quarterly profit",
                "description": "Demand remains exceptionally strong.",
                "source": "TechDaily",
                "published_at": self.df_ohlcv['date'].iloc[-2],
                "url": "https://example.com/1",
                "sentiment": "Positive",
                "sentiment_score": 0.88
            },
            {
                "ticker": "AAPL",
                "headline": "Tech sector faces mild regulatory scrutiny and market dip",
                "description": "Investors show caution.",
                "source": "MarketWatch",
                "published_at": self.df_ohlcv['date'].iloc[-1],
                "url": "https://example.com/2",
                "sentiment": "Negative",
                "sentiment_score": 0.75
            }
        ]

    def test_technical_indicators(self):
        df_ind = add_technical_indicators(self.df_ohlcv)
        # Check required columns
        for col in ['sma_20', 'sma_50', 'ema_12', 'ema_20', 'ema_26', 'rsi', 'macd', 'bbands_upper', 'bbands_lower']:
            self.assertIn(col, df_ind.columns)

        # Check RSI is bounded between 0 and 100
        self.assertTrue((df_ind['rsi'] >= 0).all() and (df_ind['rsi'] <= 100).all())

        # Check Bollinger Bands relationship: Upper >= Middle >= Lower
        self.assertTrue((df_ind['bbands_upper'] >= df_ind['bbands_lower']).all())

    def test_sentiment_analysis(self):
        pos_label, pos_score = analyze_sentiment_lexicon("Record quarterly profit and strong growth")
        neg_label, neg_score = analyze_sentiment_lexicon("Severe loss and economic crisis with heavy drop")

        self.assertEqual(pos_label, "Positive")
        self.assertEqual(neg_label, "Negative")
        self.assertGreater(pos_score, 0.5)

        overview = get_sentiment_overview("AAPL", self.sample_articles)
        self.assertEqual(overview["total_articles"], 2)
        self.assertEqual(overview["positive_count"], 1)
        self.assertEqual(overview["negative_count"], 1)

    def test_combined_feature_matrix(self):
        df_features = build_combined_feature_matrix(self.df_ohlcv, self.sample_articles)
        for col in FEATURE_COLUMNS:
            self.assertIn(col, df_features.columns)
        self.assertEqual(len(FEATURE_COLUMNS), 12)

    def test_lstm_sequence_generation(self):
        df_features = build_combined_feature_matrix(self.df_ohlcv, self.sample_articles)
        prepared = prepare_lstm_sequences(df_features, lookback_window=60, train_split=0.8)

        X_train = prepared["X_train"]
        y_train = prepared["y_train"]
        X_test = prepared["X_test"]
        latest_seq = prepared["latest_sequence"]

        # Input shape check: [N, 60, 12]
        self.assertEqual(X_train.shape[1], 60)
        self.assertEqual(X_train.shape[2], 12)
        self.assertEqual(X_test.shape[1], 60)
        self.assertEqual(X_test.shape[2], 12)
        self.assertEqual(latest_seq.shape, (1, 60, 12))

    def test_lstm_model_training_and_evaluation(self):
        df_features = build_combined_feature_matrix(self.df_ohlcv, self.sample_articles)
        prepared = prepare_lstm_sequences(df_features, lookback_window=60, train_split=0.8)

        results = train_and_evaluate_lstm(prepared, epochs=5, batch_size=16)

        # Metrics verification
        self.assertIn("mae", results)
        self.assertIn("rmse", results)
        self.assertIn("mape", results)
        self.assertIn("predicted_next_close", results)
        self.assertGreater(results["mae"], 0.0)
        self.assertGreater(results["rmse"], 0.0)
        self.assertGreater(results["predicted_next_close"], 0.0)

if __name__ == "__main__":
    unittest.main()
