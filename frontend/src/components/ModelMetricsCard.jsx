import React from 'react';
import { Gauge, CheckCircle2, Layers, Cpu, Compass } from 'lucide-react';

export default function ModelMetricsCard({ metrics }) {
  if (!metrics) return null;

  return (
    <div className="bg-[#111827] border border-gray-800 rounded-2xl p-5 shadow-xl">
      <div className="flex items-center justify-between pb-3 border-b border-gray-800">
        <div className="flex items-center gap-2">
          <Gauge className="h-5 w-5 text-indigo-400" />
          <h3 className="font-bold text-white text-sm">Model Evaluation Metrics</h3>
        </div>
        <span className="text-xs text-slate-400 bg-gray-800/80 px-2 py-0.5 rounded border border-gray-700">
          Unseen Test Horizon
        </span>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-3 gap-3 my-4">
        {/* MAE */}
        <div className="bg-[#162035]/80 p-3 rounded-xl border border-gray-800 text-center">
          <span className="text-[11px] text-slate-400 block font-medium">MAE</span>
          <span className="text-lg font-extrabold text-blue-400">{metrics.mae?.toFixed(2)}</span>
          <span className="text-[10px] text-slate-400 block mt-0.5">Mean Absolute Error</span>
        </div>

        {/* RMSE */}
        <div className="bg-[#162035]/80 p-3 rounded-xl border border-gray-800 text-center">
          <span className="text-[11px] text-slate-400 block font-medium">RMSE</span>
          <span className="text-lg font-extrabold text-cyan-400">{metrics.rmse?.toFixed(2)}</span>
          <span className="text-[10px] text-slate-400 block mt-0.5">Root Mean Squared</span>
        </div>

        {/* MAPE */}
        <div className="bg-[#162035]/80 p-3 rounded-xl border border-gray-800 text-center">
          <span className="text-[11px] text-slate-400 block font-medium">MAPE</span>
          <span className="text-lg font-extrabold text-emerald-400">{metrics.mape?.toFixed(2)}%</span>
          <span className="text-[10px] text-slate-400 block mt-0.5">Mean Abs % Error</span>
        </div>
      </div>

      {/* Model Spec List */}
      <div className="space-y-2 pt-2 border-t border-gray-800/60 text-xs">
        <div className="flex items-center justify-between text-slate-300">
          <span className="text-slate-400 flex items-center gap-1.5">
            <Compass className="h-3.5 w-3.5 text-blue-400" /> Historical Lookback Window:
          </span>
          <span className="font-semibold text-slate-200">{metrics.lookback_window || 60} Trading Days</span>
        </div>

        <div className="flex items-center justify-between text-slate-300">
          <span className="text-slate-400 flex items-center gap-1.5">
            <Layers className="h-3.5 w-3.5 text-purple-400" /> Integrated Feature Dimension:
          </span>
          <span className="font-semibold text-slate-200">{metrics.features_count || 12} Features</span>
        </div>

        <div className="flex items-center justify-between text-slate-300">
          <span className="text-slate-400 flex items-center gap-1.5">
            <Cpu className="h-3.5 w-3.5 text-indigo-400" /> Deep Learning Architecture:
          </span>
          <span className="font-semibold text-slate-200 text-[11px]">2-Layer LSTM + Dropout(0.2) + Dense</span>
        </div>
      </div>
    </div>
  );
}
