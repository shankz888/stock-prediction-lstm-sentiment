import React from 'react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend
} from 'recharts';
import { GitCompare, Info } from 'lucide-react';

export default function ActualVsPredictedChart({ data, ticker, currency }) {
  if (!data || data.length === 0) {
    return (
      <div className="bg-[#111827] border border-gray-800 rounded-2xl p-6 text-center text-slate-400">
        No evaluation data available. Run model prediction to view comparison.
      </div>
    );
  }

  const currSymbol = currency === 'INR' ? '₹' : '$';

  // Calculate domain min and max for clean scaling
  const allValues = data
    .flatMap((d) => [d.actual, d.predicted])
    .filter((v) => v !== null && v !== undefined && !isNaN(v));

  const minVal = allValues.length ? Math.floor(Math.min(...allValues) * 0.98) : 'auto';
  const maxVal = allValues.length ? Math.ceil(Math.max(...allValues) * 1.02) : 'auto';

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const actualItem = payload.find((p) => p.dataKey === 'actual');
      const predItem = payload.find((p) => p.dataKey === 'predicted');
      const isForecastPoint = !actualItem || actualItem.value === null;

      return (
        <div className="bg-[#0B0F19] border border-gray-700 p-3 rounded-xl shadow-2xl text-xs space-y-1.5">
          <p className="font-semibold text-slate-200 border-b border-gray-800 pb-1 flex items-center justify-between gap-4">
            <span>Date: {label}</span>
            {isForecastPoint && (
              <span className="text-[10px] text-amber-400 bg-amber-400/10 px-1.5 py-0.5 rounded border border-amber-400/30">
                Future Forecast
              </span>
            )}
          </p>

          {actualItem && actualItem.value !== null && (
            <div className="flex items-center justify-between gap-4 text-emerald-400">
              <span className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 inline-block" />
                Actual Close:
              </span>
              <span className="font-mono font-bold">{currSymbol}{actualItem.value?.toFixed(2)}</span>
            </div>
          )}

          {predItem && (
            <div className="flex items-center justify-between gap-4 text-blue-400">
              <span className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-blue-400 inline-block" />
                LSTM Predicted:
              </span>
              <span className="font-mono font-bold">{currSymbol}{predItem.value?.toFixed(2)}</span>
            </div>
          )}

          {actualItem && actualItem.value !== null && predItem && (
            <div className="pt-1 border-t border-gray-800 text-slate-400 flex items-center justify-between text-[11px]">
              <span>Absolute Difference:</span>
              <span className="font-mono font-medium text-slate-300">
                {currSymbol}{Math.abs(actualItem.value - predItem.value).toFixed(2)}
              </span>
            </div>
          )}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="bg-[#111827] border border-gray-800 rounded-2xl p-5 shadow-xl">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-4">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <GitCompare className="h-4 w-4" />
          </div>
          <div>
            <h3 className="font-bold text-white text-base">Actual vs Predicted Closing Price</h3>
            <p className="text-xs text-slate-400">
              Chronological test period comparison + next trading day target
            </p>
          </div>
        </div>

        <div className="flex items-center gap-4 text-xs font-medium">
          <div className="flex items-center gap-1.5">
            <div className="w-3 h-0.5 bg-emerald-400 rounded" />
            <span className="text-slate-300">Actual Price</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-3 h-0.5 bg-blue-400 border-dashed border-t border-blue-400" />
            <span className="text-slate-300">LSTM Predicted</span>
          </div>
        </div>
      </div>

      <div className="h-72 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1F2937" vertical={false} />
            <XAxis
              dataKey="date"
              stroke="#6B7280"
              fontSize={11}
              tickLine={false}
              tickFormatter={(v) => (v ? v.slice(5) : '')}
            />
            <YAxis
              stroke="#6B7280"
              fontSize={11}
              domain={[minVal, maxVal]}
              tickLine={false}
              axisLine={false}
              tickFormatter={(val) => `${currSymbol}${val}`}
            />
            <Tooltip content={<CustomTooltip />} />
            <Line
              type="monotone"
              dataKey="actual"
              stroke="#10B981"
              strokeWidth={2.5}
              dot={{ r: 2.5, fill: '#10B981' }}
              activeDot={{ r: 5, stroke: '#fff', strokeWidth: 1 }}
              name="Actual Close"
            />
            <Line
              type="monotone"
              dataKey="predicted"
              stroke="#3B82F6"
              strokeWidth={2}
              strokeDasharray="4 4"
              dot={{ r: 2, fill: '#3B82F6' }}
              activeDot={{ r: 5, stroke: '#fff', strokeWidth: 1 }}
              name="LSTM Predicted"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="mt-3 flex items-center justify-between text-[11px] text-slate-400 pt-3 border-t border-gray-800">
        <span className="flex items-center gap-1">
          <Info className="h-3.5 w-3.5 text-blue-400" /> Evaluated strictly on chronologically held-out test data
        </span>
        <span className="font-mono text-slate-400">{data.length} test points</span>
      </div>
    </div>
  );
}
