import unittest
from fastapi.testclient import TestClient
from backend.app.main import app

class TestAPIEndpoints(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_root_and_health(self):
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("service", resp.json())

        resp_health = self.client.get("/health")
        self.assertEqual(resp_health.status_code, 200)
        self.assertEqual(resp_health.json()["status"], "healthy")

    def test_stock_quote(self):
        resp = self.client.get("/stock/AAPL")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["ticker"], "AAPL")
        self.assertIn("current_price", data)
        self.assertIn("daily_change", data)
        self.assertIn("volume", data)

    def test_stock_history(self):
        resp = self.client.get("/stock/AAPL/history?period=1y")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["ticker"], "AAPL")
        self.assertGreater(data["total_records"], 50)
        first_row = data["data"][0]
        for key in ["date", "open", "high", "low", "close", "volume"]:
            self.assertIn(key, first_row)

    def test_stock_indicators(self):
        resp = self.client.get("/stock/AAPL/indicators?period=1y")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertGreater(len(data["indicators"]), 50)
        row = data["indicators"][-1]
        self.assertIn("sma_20", row)
        self.assertIn("rsi", row)
        self.assertIn("macd", row)
        self.assertIn("bbands_upper", row)

    def test_news_and_sentiment(self):
        resp_news = self.client.get("/news/AAPL?limit=10")
        self.assertEqual(resp_news.status_code, 200)
        articles = resp_news.json()
        self.assertGreater(len(articles), 0)
        self.assertIn("sentiment", articles[0])
        self.assertIn(articles[0]["sentiment"], ["Positive", "Neutral", "Negative"])

        resp_sent = self.client.get("/news/AAPL/sentiment?limit=15")
        self.assertEqual(resp_sent.status_code, 200)
        sent_data = resp_sent.json()
        self.assertIn("positive_pct", sent_data)
        self.assertIn("daily_sentiment", sent_data)

    def test_prediction_and_metrics(self):
        resp_pred = self.client.get("/predict/AAPL?period=1y")
        self.assertEqual(resp_pred.status_code, 200)
        data = resp_pred.json()
        self.assertEqual(data["ticker"], "AAPL")
        self.assertIn("predicted_price", data)
        self.assertIn("predicted_change", data)
        self.assertIn("metrics", data)
        self.assertIn("mae", data["metrics"])
        self.assertIn("rmse", data["metrics"])
        self.assertIn("mape", data["metrics"])
        self.assertGreater(len(data["actual_vs_predicted"]), 0)

        # Check metrics endpoint
        resp_metrics = self.client.get("/model/metrics?ticker=AAPL")
        self.assertEqual(resp_metrics.status_code, 200)
        metrics = resp_metrics.json()
        self.assertIn("mae", metrics)
        self.assertIn("rmse", metrics)
        self.assertIn("mape", metrics)

if __name__ == "__main__":
    unittest.main()
