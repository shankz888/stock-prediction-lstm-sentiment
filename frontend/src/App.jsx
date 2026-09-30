import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import StockSummaryCard from './components/StockSummaryCard';
import PredictionCard from './components/PredictionCard';
import ModelMetricsCard from './components/ModelMetricsCard';
import ActualVsPredictedChart from './components/ActualVsPredictedChart';
import TechnicalIndicatorsChart from './components/TechnicalIndicatorsChart';
import SentimentDashboard from './components/SentimentDashboard';
import NewsList from './components/NewsList';
import { api } from './services/api';
import { AlertTriangle, Loader2 } from 'lucide-react';

export default function App() {
  const [currentTicker, setCurrentTicker] = useState('AAPL');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Application Data States
  const [quote, setQuote] = useState(null);
  const [indicators, setIndicators] = useState([]);
  const [sentiment, setSentiment] = useState(null);
  const [prediction, setPrediction] = useState(null);

  const fetchAllData = async (ticker) => {
    setLoading(true);
    setError(null);
    try {
      // 1. Fetch Quote
      const quoteData = await api.getQuote(ticker);
      setQuote(quoteData);

      // 2. Fetch Indicators
      const indData = await api.getIndicators(ticker, '1y');
      setIndicators(indData.indicators || []);

      // 3. Fetch News & Sentiment
      const sentData = await api.getSentiment(ticker, 25);
      setSentiment(sentData);

      // 4. Fetch LSTM Prediction
      const predData = await api.getPrediction(ticker, '2y');
      setPrediction(predData);

    } catch (err) {
      console.error("Dashboard data load error:", err);
      setError(err.message || "Failed to retrieve stock data or execute prediction model.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAllData(currentTicker);
  }, [currentTicker]);

  const handleSelectTicker = (ticker) => {
    setCurrentTicker(ticker);
  };

  const handleRefresh = () => {
    fetchAllData(currentTicker);
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#0B0F19] text-slate-100">
      {/* Top Navigation & Search */}
      <Navbar
        currentTicker={currentTicker}
        onSelectTicker={handleSelectTicker}
        onRefresh={handleRefresh}
        loading={loading}
      />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
        
        {/* Error Banner */}
        {error && (
          <div className="bg-rose-500/10 border border-rose-500/30 text-rose-300 p-4 rounded-xl flex items-start gap-3 shadow-lg">
            <AlertTriangle className="h-5 w-5 text-rose-400 shrink-0 mt-0.5" />
            <div>
              <h4 className="font-semibold text-rose-200">Unable to complete request</h4>
              <p className="text-xs text-rose-300/80 mt-0.5">{error}</p>
            </div>
          </div>
        )}

        {/* Loading Overlay or State */}
        {loading && !quote && (
          <div className="flex flex-col items-center justify-center py-24 space-y-4">
            <Loader2 className="h-10 w-10 text-blue-500 animate-spin" />
            <div className="text-center">
              <p className="text-base font-semibold text-white">Analyzing Market Data & Running FinBERT + LSTM</p>
              <p className="text-xs text-slate-400 mt-1">Collecting OHLCV, calculating indicators, scoring news, and training sequence model...</p>
            </div>
          </div>
        )}

        {/* Dashboard Content */}
        {quote && (
          <>
            {/* 1. Stock Overview Card */}
            <StockSummaryCard quote={quote} />

            {/* 2. Prediction & Model Metrics Cards Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
              <div className="lg:col-span-7">
                <PredictionCard prediction={prediction} />
              </div>
              <div className="lg:col-span-5">
                <ModelMetricsCard metrics={prediction?.metrics} />
              </div>
            </div>

            {/* 3. Actual vs Predicted Interactive Chart */}
            <ActualVsPredictedChart
              data={prediction?.actual_vs_predicted || []}
              ticker={currentTicker}
              currency={quote.currency}
            />

            {/* 4. Technical Indicators Multi-Tab Chart */}
            <TechnicalIndicatorsChart
              indicators={indicators}
              currency={quote.currency}
            />

            {/* 5. FinBERT Sentiment & News Feed Section */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
              <div className="lg:col-span-5">
                <SentimentDashboard sentiment={sentiment} />
              </div>
              <div className="lg:col-span-7">
                <NewsList
                  articles={sentiment?.articles || []}
                  ticker={currentTicker}
                />
              </div>
            </div>
          </>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-gray-800 bg-[#0E1526]/80 py-6 text-center text-xs text-slate-400 mt-12">
        <div className="max-w-7xl mx-auto px-4 space-y-2">
          <p className="font-medium text-slate-300">
            Stock Price Prediction Using LSTM with News Sentiment Analysis (FinBERT)
          </p>
          <p className="text-slate-400 text-[11px] max-w-2xl mx-auto">
            Educational & Analytical Platform • Technical Indicators (SMA, EMA, RSI, MACD, Bollinger Bands) + FinBERT Sentiment Aggregation + 2-Layer LSTM Time-Series Architecture.
          </p>
          <p className="text-[10px] text-slate-400">
            Intended exclusively for educational, research, and machine learning experimentation. Not financial advice.
          </p>
        </div>
      </footer>
    </div>
  );
}
