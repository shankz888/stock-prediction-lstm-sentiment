import React from 'react';
import { ArrowUpRight, ArrowDownRight, Activity, DollarSign, BarChart2 } from 'lucide-react';

export default function StockSummaryCard({ quote }) {
  if (!quote) return null;

  const isPositive = quote.daily_change >= 0;
  const currSymbol = quote.currency === 'INR' ? '₹' : '$';

  const formatVolume = (vol) => {
    if (!vol) return 'N/A';
    if (vol >= 1e9) return (vol / 1e9).toFixed(2) + 'B';
    if (vol >= 1e6) return (vol / 1e6).toFixed(2) + 'M';
    if (vol >= 1e3) return (vol / 1e3).toFixed(1) + 'K';
    return vol.toLocaleString();
  };

  return (
    <div className="bg-[#111827] border border-gray-800 rounded-2xl p-5 shadow-xl">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        
        {/* Left: Company & Ticker */}
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xs uppercase font-semibold tracking-wider text-blue-400 bg-blue-500/10 px-2 py-0.5 rounded border border-blue-500/20">
              {quote.ticker}
            </span>
            <span className="text-xs text-slate-400">Market Equity</span>
          </div>
          <h2 className="text-xl sm:text-2xl font-bold text-white mt-1">
            {quote.company_name}
          </h2>
        </div>

        {/* Right: Current Price & Daily Change */}
        <div className="flex sm:flex-col items-baseline sm:items-end justify-between sm:justify-center">
          <div className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            {currSymbol}{quote.current_price?.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </div>
          <div className={`flex items-center text-sm font-semibold gap-1 mt-0.5 ${
            isPositive ? 'text-emerald-400' : 'text-rose-400'
          }`}>
            {isPositive ? <ArrowUpRight className="h-4 w-4" /> : <ArrowDownRight className="h-4 w-4" />}
            <span>{isPositive ? '+' : ''}{quote.daily_change}</span>
            <span>({isPositive ? '+' : ''}{quote.daily_change_percent}%)</span>
          </div>
        </div>
      </div>

      {/* Secondary Stats Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-5 pt-4 border-t border-gray-800/80 text-xs">
        <div className="bg-[#162035]/60 p-2.5 rounded-lg border border-gray-800">
          <span className="text-slate-400 block mb-0.5 flex items-center gap-1">
            <BarChart2 className="h-3 w-3 text-blue-400" /> Volume
          </span>
          <span className="font-semibold text-slate-200">{formatVolume(quote.volume)}</span>
        </div>

        <div className="bg-[#162035]/60 p-2.5 rounded-lg border border-gray-800">
          <span className="text-slate-400 block mb-0.5">Day High</span>
          <span className="font-semibold text-slate-200">
            {quote.day_high ? `${currSymbol}${quote.day_high}` : '—'}
          </span>
        </div>

        <div className="bg-[#162035]/60 p-2.5 rounded-lg border border-gray-800">
          <span className="text-slate-400 block mb-0.5">Day Low</span>
          <span className="font-semibold text-slate-200">
            {quote.day_low ? `${currSymbol}${quote.day_low}` : '—'}
          </span>
        </div>

        <div className="bg-[#162035]/60 p-2.5 rounded-lg border border-gray-800">
          <span className="text-slate-400 block mb-0.5">Prev Close</span>
          <span className="font-semibold text-slate-200">
            {quote.previous_close ? `${currSymbol}${quote.previous_close}` : '—'}
          </span>
        </div>
      </div>
    </div>
  );
}
