import React from 'react';
import { BrainCircuit, TrendingUp, TrendingDown, Minus, Calendar, ShieldAlert } from 'lucide-react';

export default function PredictionCard({ prediction }) {
  if (!prediction) return null;

  const isUp = prediction.predicted_change >= 0;
  const currSymbol = prediction.currency === 'INR' ? '₹' : '$';

  return (
    <div className="bg-gradient-to-br from-[#111827] via-[#131d36] to-[#0f172a] border border-blue-500/30 rounded-2xl p-6 shadow-2xl relative overflow-hidden">
      {/* Background glow accent */}
      <div className="absolute -top-16 -right-16 w-44 h-44 bg-blue-500/10 rounded-full blur-3xl pointer-events-none" />

      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-lg bg-blue-500/20 text-blue-400 border border-blue-500/30">
            <BrainCircuit className="h-5 w-5" />
          </div>
          <div>
            <h3 className="font-bold text-white text-base">Next-Day LSTM Prediction</h3>
            <p className="text-xs text-slate-400">Integrated Market Indicators & FinBERT Sentiment</p>
          </div>
        </div>

        <div className="flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wider border shadow-sm"
          style={{
            backgroundColor: prediction.signal === 'Bullish' ? 'rgba(16, 185, 129, 0.15)' : prediction.signal === 'Bearish' ? 'rgba(239, 68, 68, 0.15)' : 'rgba(100, 116, 139, 0.2)',
            color: prediction.signal === 'Bullish' ? '#34D399' : prediction.signal === 'Bearish' ? '#F87171' : '#94A3B8',
            borderColor: prediction.signal === 'Bullish' ? 'rgba(16, 185, 129, 0.3)' : prediction.signal === 'Bearish' ? 'rgba(239, 68, 68, 0.3)' : 'rgba(100, 116, 139, 0.3)'
          }}
        >
          {prediction.signal === 'Bullish' && <TrendingUp className="h-3.5 w-3.5" />}
          {prediction.signal === 'Bearish' && <TrendingDown className="h-3.5 w-3.5" />}
          {prediction.signal === 'Neutral' && <Minus className="h-3.5 w-3.5" />}
          <span>{prediction.signal} Signal</span>
        </div>
      </div>

      {/* Main Forecast Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-6">
        {/* Current Price */}
        <div className="bg-[#0B0F19]/60 p-4 rounded-xl border border-gray-800">
          <span className="text-xs text-slate-400 block mb-1">Current Closing Price</span>
          <div className="text-2xl font-bold text-slate-200">
            {currSymbol}{prediction.current_price?.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </div>
          <span className="text-[11px] text-slate-400 mt-1 block">Baseline reference</span>
        </div>

        {/* Predicted Price */}
        <div className="bg-[#0B0F19]/90 p-4 rounded-xl border border-blue-500/40 shadow-inner">
          <span className="text-xs text-blue-400 font-medium block mb-1">Predicted Closing Price</span>
          <div className="text-2xl font-extrabold text-white">
            {currSymbol}{prediction.predicted_price?.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </div>
          <span className="text-[11px] text-slate-400 mt-1 flex items-center gap-1">
            <Calendar className="h-3 w-3 text-blue-400" /> Horizon: Next Trading Day
          </span>
        </div>

        {/* Expected Change */}
        <div className="bg-[#0B0F19]/60 p-4 rounded-xl border border-gray-800">
          <span className="text-xs text-slate-400 block mb-1">Expected Change</span>
          <div className={`text-2xl font-bold flex items-center gap-1 ${
            isUp ? 'text-emerald-400' : 'text-rose-400'
          }`}>
            <span>{isUp ? '+' : ''}{currSymbol}{Math.abs(prediction.predicted_change).toFixed(2)}</span>
          </div>
          <span className={`text-xs font-semibold block mt-1 ${isUp ? 'text-emerald-400' : 'text-rose-400'}`}>
            ({isUp ? '+' : ''}{prediction.predicted_change_percent?.toFixed(2)}%)
          </span>
        </div>
      </div>

      {/* Educational Notice */}
      <div className="mt-4 pt-3 border-t border-gray-800/80 flex items-start gap-2 text-[11px] text-slate-400">
        <ShieldAlert className="h-3.5 w-3.5 text-amber-400 shrink-0 mt-0.5" />
        <span>
          Educational & analytical model forecast. Produced by a 60-day lookback LSTM with daily FinBERT sentiment; does not guarantee future prices.
        </span>
      </div>
    </div>
  );
}
