const API_BASE = 'http://localhost:8000';

async function fetchJson(endpoint) {
  const res = await fetch(`${API_BASE}${endpoint}`);
  if (!res.ok) {
    let errorDetail = `Request failed: ${res.status}`;
    try {
      const err = await res.json();
      errorDetail = err.detail || errorDetail;
    } catch (_) {}
    throw new Error(errorDetail);
  }
  return res.json();
}

export const api = {
  // Stock Quote
  getQuote: (ticker) => fetchJson(`/stock/${encodeURIComponent(ticker)}`),

  // Historical OHLCV
  getHistory: (ticker, period = '1y') => 
    fetchJson(`/stock/${encodeURIComponent(ticker)}/history?period=${period}`),

  // Technical Indicators
  getIndicators: (ticker, period = '1y') =>
    fetchJson(`/stock/${encodeURIComponent(ticker)}/indicators?period=${period}`),

  // Recent News
  getNews: (ticker, limit = 25) =>
    fetchJson(`/news/${encodeURIComponent(ticker)}?limit=${limit}`),

  // Sentiment Breakdown
  getSentiment: (ticker, limit = 30) =>
    fetchJson(`/news/${encodeURIComponent(ticker)}/sentiment?limit=${limit}`),

  // LSTM Prediction
  getPrediction: (ticker, period = '2y') =>
    fetchJson(`/predict/${encodeURIComponent(ticker)}?period=${period}`),

  // Global / Ticker Model Metrics
  getModelMetrics: (ticker = '') =>
    fetchJson(ticker ? `/model/metrics?ticker=${encodeURIComponent(ticker)}` : '/model/metrics'),
};
