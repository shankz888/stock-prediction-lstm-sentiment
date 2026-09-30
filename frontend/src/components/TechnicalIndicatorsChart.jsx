import React, { useState } from 'react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ReferenceLine,
  Cell
} from 'recharts';
import { Sliders, Activity, TrendingUp, Layers } from 'lucide-react';

export default function TechnicalIndicatorsChart({ indicators, currency }) {
  const [activeTab, setActiveTab] = useState('price_ma'); // 'price_ma', 'bbands', 'rsi', 'macd', 'volume'

  if (!indicators || indicators.length === 0) {
    return (
      <div className="bg-[#111827] border border-gray-800 rounded-2xl p-6 text-center text-slate-400">
        Loading technical indicators...
      </div>
    );
  }

  const currSymbol = currency === 'INR' ? '₹' : '$';

  // Slice to most recent 90-120 days for readable charts
  const displayData = indicators.slice(-90);

  const CustomIndicatorTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-[#0B0F19] border border-gray-700 p-3 rounded-xl shadow-2xl text-xs space-y-1">
          <p className="font-semibold text-slate-200 border-b border-gray-800 pb-1">
            Date: {label}
          </p>
          {payload.map((item, idx) => (
            <div key={idx} className="flex items-center justify-between gap-4" style={{ color: item.color || item.fill }}>
              <span className="flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full inline-block" style={{ backgroundColor: item.color || item.fill }} />
                {item.name}:
              </span>
              <span className="font-mono font-bold">
                {typeof item.value === 'number' ? item.value.toFixed(2) : item.value}
              </span>
            </div>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="bg-[#111827] border border-gray-800 rounded-2xl p-5 shadow-xl">
      {/* Header & Tabs */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 mb-4">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-lg bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
            <Sliders className="h-4 w-4" />
          </div>
          <div>
            <h3 className="font-bold text-white text-base">Technical Indicator Engine</h3>
            <p className="text-xs text-slate-400">Derived mathematical features feeding the LSTM</p>
          </div>
        </div>

        {/* Tab Controls */}
        <div className="flex items-center gap-1 bg-[#162035] p-1 rounded-xl border border-gray-800 overflow-x-auto text-xs font-medium">
          <button
            onClick={() => setActiveTab('price_ma')}
            className={`px-3 py-1.5 rounded-lg transition whitespace-nowrap ${
              activeTab === 'price_ma' ? 'bg-blue-600 text-white font-semibold' : 'text-slate-400 hover:text-white'
            }`}
          >
            SMA & EMA
          </button>
          <button
            onClick={() => setActiveTab('bbands')}
            className={`px-3 py-1.5 rounded-lg transition whitespace-nowrap ${
              activeTab === 'bbands' ? 'bg-blue-600 text-white font-semibold' : 'text-slate-400 hover:text-white'
            }`}
          >
            Bollinger Bands
          </button>
          <button
            onClick={() => setActiveTab('rsi')}
            className={`px-3 py-1.5 rounded-lg transition whitespace-nowrap ${
              activeTab === 'rsi' ? 'bg-blue-600 text-white font-semibold' : 'text-slate-400 hover:text-white'
            }`}
          >
            RSI (14)
          </button>
          <button
            onClick={() => setActiveTab('macd')}
            className={`px-3 py-1.5 rounded-lg transition whitespace-nowrap ${
              activeTab === 'macd' ? 'bg-blue-600 text-white font-semibold' : 'text-slate-400 hover:text-white'
            }`}
          >
            MACD
          </button>
          <button
            onClick={() => setActiveTab('volume')}
            className={`px-3 py-1.5 rounded-lg transition whitespace-nowrap ${
              activeTab === 'volume' ? 'bg-blue-600 text-white font-semibold' : 'text-slate-400 hover:text-white'
            }`}
          >
            Volume
          </button>
        </div>
      </div>

      {/* Chart Canvas */}
      <div className="h-72 w-full">
        {/* Tab 1: SMA & EMA */}
        {activeTab === 'price_ma' && (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={displayData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1F2937" vertical={false} />
              <XAxis dataKey="date" stroke="#6B7280" fontSize={11} tickFormatter={(v) => v?.slice(5)} />
              <YAxis stroke="#6B7280" fontSize={11} domain={['auto', 'auto']} tickFormatter={(v) => `${currSymbol}${v}`} />
              <Tooltip content={<CustomIndicatorTooltip />} />
              <Line type="monotone" dataKey="close" stroke="#FFFFFF" strokeWidth={2} dot={false} name="Close" />
              <Line type="monotone" dataKey="sma_20" stroke="#3B82F6" strokeWidth={1.5} dot={false} name="SMA 20" />
              <Line type="monotone" dataKey="sma_50" stroke="#F59E0B" strokeWidth={1.5} dot={false} name="SMA 50" />
              <Line type="monotone" dataKey="ema_12" stroke="#10B981" strokeWidth={1.5} strokeDasharray="3 3" dot={false} name="EMA 12" />
              <Line type="monotone" dataKey="ema_26" stroke="#EC4899" strokeWidth={1.5} strokeDasharray="3 3" dot={false} name="EMA 26" />
            </LineChart>
          </ResponsiveContainer>
        )}

        {/* Tab 2: Bollinger Bands */}
        {activeTab === 'bbands' && (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={displayData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1F2937" vertical={false} />
              <XAxis dataKey="date" stroke="#6B7280" fontSize={11} tickFormatter={(v) => v?.slice(5)} />
              <YAxis stroke="#6B7280" fontSize={11} domain={['auto', 'auto']} tickFormatter={(v) => `${currSymbol}${v}`} />
              <Tooltip content={<CustomIndicatorTooltip />} />
              <Line type="monotone" dataKey="bbands_upper" stroke="#EF4444" strokeWidth={1.5} dot={false} name="Upper Band (+2σ)" />
              <Line type="monotone" dataKey="bbands_middle" stroke="#3B82F6" strokeWidth={1.5} strokeDasharray="4 4" dot={false} name="Middle (SMA 20)" />
              <Line type="monotone" dataKey="bbands_lower" stroke="#10B981" strokeWidth={1.5} dot={false} name="Lower Band (-2σ)" />
              <Line type="monotone" dataKey="close" stroke="#F3F4F6" strokeWidth={2} dot={false} name="Close Price" />
            </LineChart>
          </ResponsiveContainer>
        )}

        {/* Tab 3: RSI (14) */}
        {activeTab === 'rsi' && (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={displayData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1F2937" vertical={false} />
              <XAxis dataKey="date" stroke="#6B7280" fontSize={11} tickFormatter={(v) => v?.slice(5)} />
              <YAxis stroke="#6B7280" fontSize={11} domain={[0, 100]} ticks={[0, 30, 50, 70, 100]} />
              <Tooltip content={<CustomIndicatorTooltip />} />
              <ReferenceLine y={70} stroke="#EF4444" strokeDasharray="3 3" label={{ value: 'Overbought (70)', fill: '#EF4444', fontSize: 10 }} />
              <ReferenceLine y={30} stroke="#10B981" strokeDasharray="3 3" label={{ value: 'Oversold (30)', fill: '#10B981', fontSize: 10 }} />
              <ReferenceLine y={50} stroke="#6B7280" strokeDasharray="2 2" />
              <Line type="monotone" dataKey="rsi" stroke="#8B5CF6" strokeWidth={2} dot={false} name="RSI (14)" />
            </LineChart>
          </ResponsiveContainer>
        )}

        {/* Tab 4: MACD */}
        {activeTab === 'macd' && (
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={displayData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1F2937" vertical={false} />
              <XAxis dataKey="date" stroke="#6B7280" fontSize={11} tickFormatter={(v) => v?.slice(5)} />
              <YAxis stroke="#6B7280" fontSize={11} domain={['auto', 'auto']} />
              <Tooltip content={<CustomIndicatorTooltip />} />
              <ReferenceLine y={0} stroke="#4B5563" />
              <Bar dataKey="macd_hist" name="Histogram">
                {displayData.map((entry, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={(entry.macd_hist || 0) >= 0 ? '#10B981' : '#EF4444'}
                  />
                ))}
              </Bar>
              <Line type="monotone" dataKey="macd" stroke="#3B82F6" strokeWidth={1.8} dot={false} name="MACD Line" />
              <Line type="monotone" dataKey="macd_signal" stroke="#F59E0B" strokeWidth={1.8} dot={false} name="Signal Line" />
            </BarChart>
          </ResponsiveContainer>
        )}

        {/* Tab 5: Volume */}
        {activeTab === 'volume' && (
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={displayData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1F2937" vertical={false} />
              <XAxis dataKey="date" stroke="#6B7280" fontSize={11} tickFormatter={(v) => v?.slice(5)} />
              <YAxis stroke="#6B7280" fontSize={11} tickFormatter={(v) => (v >= 1e6 ? `${(v/1e6).toFixed(1)}M` : v)} />
              <Tooltip content={<CustomIndicatorTooltip />} />
              <Bar dataKey="volume" fill="#3B82F6" opacity={0.8} name="Trading Volume" />
            </BarChart>
          </ResponsiveContainer>
        )}
      </div>

      {/* Legend & Summary Info */}
      <div className="mt-3 pt-3 border-t border-gray-800 text-[11px] text-slate-400 flex flex-wrap items-center justify-between gap-2">
        <span className="flex items-center gap-1.5">
          <Activity className="h-3.5 w-3.5 text-blue-400" />
          {activeTab === 'price_ma' && 'Showing Close Price with 20/50 Simple and 12/26 Exponential Moving Averages'}
          {activeTab === 'bbands' && '20-day Simple Moving Average enveloped by ±2.0 Rolling Standard Deviations'}
          {activeTab === 'rsi' && '14-period Relative Strength Index oscillator (Values >70 overbought, <30 oversold)'}
          {activeTab === 'macd' && 'Moving Average Convergence Divergence (12 EMA - 26 EMA) and 9 EMA Signal'}
          {activeTab === 'volume' && 'Daily market participant share turnover and trading liquidity'}
        </span>
        <span className="font-mono text-slate-400">90 Trading Days Displayed</span>
      </div>
    </div>
  );
}
