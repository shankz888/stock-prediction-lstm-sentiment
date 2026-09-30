import React, { useState } from 'react';
import { Search, TrendingUp, Cpu, RefreshCw } from 'lucide-react';

const QUICK_TICKERS = [
  { symbol: 'AAPL', label: 'Apple' },
  { symbol: 'TSLA', label: 'Tesla' },
  { symbol: 'NVDA', label: 'Nvidia' },
  { symbol: 'MSFT', label: 'Microsoft' },
  { symbol: 'RELIANCE.NS', label: 'Reliance' },
  { symbol: 'TCS.NS', label: 'TCS' },
  { symbol: 'INFY.NS', label: 'Infosys' }
];

export default function Navbar({ currentTicker, onSelectTicker, onRefresh, loading }) {
  const [searchInput, setSearchInput] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (searchInput.trim()) {
      onSelectTicker(searchInput.trim().toUpperCase());
      setSearchInput('');
    }
  };

  return (
    <header className="border-b border-gray-800 bg-[#0E1526]/90 backdrop-blur sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3.5">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
          
          {/* Logo & Subtitle */}
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-xl bg-gradient-to-tr from-blue-600 via-indigo-600 to-cyan-400 flex items-center justify-center shadow-lg shadow-blue-500/20">
              <TrendingUp className="h-6 w-6 text-white" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-extrabold text-xl tracking-tight text-white">StockVision</span>
                <span className="px-2 py-0.5 text-xs font-semibold uppercase tracking-wider rounded-md bg-blue-500/20 text-blue-400 border border-blue-500/30">
                  LSTM + FinBERT
                </span>
              </div>
              <p className="text-xs text-slate-400">Stock Price Prediction & News Sentiment Analysis</p>
            </div>
          </div>

          {/* Search bar & Refresh */}
          <div className="flex items-center gap-2">
            <form onSubmit={handleSubmit} className="relative flex-1 sm:w-72">
              <input
                type="text"
                placeholder="Search ticker (e.g. AAPL, RELIANCE)..."
                value={searchInput}
                onChange={(e) => setSearchInput(e.target.value)}
                className="w-full bg-[#162035] border border-gray-700 rounded-lg pl-9 pr-4 py-2 text-sm text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
              />
              <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
            </form>

            <button
              onClick={onRefresh}
              disabled={loading}
              title="Refresh Data & Retrain Model"
              className="p-2.5 rounded-lg bg-[#162035] hover:bg-gray-800 text-slate-300 hover:text-white border border-gray-700 transition flex items-center justify-center disabled:opacity-50"
            >
              <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin text-blue-400' : ''}`} />
            </button>
          </div>
        </div>

        {/* Quick select ticker chips */}
        <div className="flex items-center gap-1.5 mt-3 overflow-x-auto pb-1 text-xs">
          <span className="text-slate-400 mr-1 flex items-center gap-1">
            <Cpu className="h-3 w-3" /> Quick Tickers:
          </span>
          {QUICK_TICKERS.map((t) => (
            <button
              key={t.symbol}
              onClick={() => onSelectTicker(t.symbol)}
              className={`px-2.5 py-1 rounded-md transition font-medium whitespace-nowrap ${
                currentTicker === t.symbol
                  ? 'bg-blue-600 text-white font-semibold shadow-sm'
                  : 'bg-[#162035] text-slate-300 hover:bg-gray-800 hover:text-white border border-gray-700/60'
              }`}
            >
              {t.label} <span className="text-[10px] opacity-70">({t.symbol})</span>
            </button>
          ))}
        </div>
      </div>
    </header>
  );
}
