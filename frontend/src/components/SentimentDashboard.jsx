import React from 'react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Cell
} from 'recharts';
import { MessageSquareText, ThumbsUp, MinusCircle, ThumbsDown, Sparkles } from 'lucide-react';

export default function SentimentDashboard({ sentiment }) {
  if (!sentiment) return null;

  const {
    total_articles = 0,
    positive_count = 0,
    neutral_count = 0,
    negative_count = 0,
    positive_pct = 0,
    neutral_pct = 0,
    negative_pct = 0,
    average_score = 0,
    daily_sentiment = []
  } = sentiment;

  const sentimentData = [
    { name: 'Positive', count: positive_count, pct: positive_pct, color: '#10B981' },
    { name: 'Neutral', count: neutral_count, pct: neutral_pct, color: '#64748B' },
    { name: 'Negative', count: negative_count, pct: negative_pct, color: '#EF4444' }
  ];

  return (
    <div className="bg-[#111827] border border-gray-800 rounded-2xl p-5 shadow-xl">
      {/* Header */}
      <div className="flex items-center justify-between pb-3 border-b border-gray-800">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-lg bg-pink-500/10 text-pink-400 border border-pink-500/20">
            <MessageSquareText className="h-4 w-4" />
          </div>
          <div>
            <h3 className="font-bold text-white text-base">FinBERT Sentiment Analytics</h3>
            <p className="text-xs text-slate-400">Natural Language Processing of financial news</p>
          </div>
        </div>

        <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-blue-500/10 text-blue-400 border border-blue-500/20 text-xs font-semibold">
          <Sparkles className="h-3.5 w-3.5" />
          <span>FinBERT NLP</span>
        </div>
      </div>

      {/* Top Stats Banner */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 my-4">
        {/* Total Articles */}
        <div className="bg-[#162035]/80 p-3 rounded-xl border border-gray-800">
          <span className="text-xs text-slate-400 block mb-0.5">Articles Analyzed</span>
          <span className="text-xl font-extrabold text-white">{total_articles}</span>
          <span className="text-[10px] text-slate-400 block">Deduplicated</span>
        </div>

        {/* Positive % */}
        <div className="bg-[#162035]/80 p-3 rounded-xl border border-emerald-900/30">
          <span className="text-xs text-emerald-400 flex items-center gap-1 mb-0.5 font-medium">
            <ThumbsUp className="h-3 w-3" /> Positive
          </span>
          <span className="text-xl font-extrabold text-emerald-400">{positive_pct}%</span>
          <span className="text-[10px] text-slate-400 block">{positive_count} articles</span>
        </div>

        {/* Neutral % */}
        <div className="bg-[#162035]/80 p-3 rounded-xl border border-gray-800">
          <span className="text-xs text-slate-300 flex items-center gap-1 mb-0.5 font-medium">
            <MinusCircle className="h-3 w-3" /> Neutral
          </span>
          <span className="text-xl font-extrabold text-slate-300">{neutral_pct}%</span>
          <span className="text-[10px] text-slate-400 block">{neutral_count} articles</span>
        </div>

        {/* Negative % */}
        <div className="bg-[#162035]/80 p-3 rounded-xl border border-rose-900/30">
          <span className="text-xs text-rose-400 flex items-center gap-1 mb-0.5 font-medium">
            <ThumbsDown className="h-3 w-3" /> Negative
          </span>
          <span className="text-xl font-extrabold text-rose-400">{negative_pct}%</span>
          <span className="text-[10px] text-slate-400 block">{negative_count} articles</span>
        </div>
      </div>

      {/* Sentiment Distribution Bar */}
      <div className="my-4">
        <div className="flex items-center justify-between text-xs text-slate-400 mb-1.5 font-medium">
          <span>Sentiment Distribution</span>
          <span>Average Score: <strong className="text-white font-mono">{average_score > 0 ? `+${average_score}` : average_score}</strong></span>
        </div>
        <div className="h-3 w-full bg-gray-800 rounded-full overflow-hidden flex shadow-inner">
          <div style={{ width: `${positive_pct}%` }} className="bg-emerald-500 transition-all duration-500" title={`Positive: ${positive_pct}%`} />
          <div style={{ width: `${neutral_pct}%` }} className="bg-slate-500 transition-all duration-500" title={`Neutral: ${neutral_pct}%`} />
          <div style={{ width: `${negative_pct}%` }} className="bg-rose-500 transition-all duration-500" title={`Negative: ${negative_pct}%`} />
        </div>
      </div>

      {/* Daily Aggregated Sentiment Timeline */}
      {daily_sentiment.length > 0 && (
        <div className="mt-5 pt-4 border-t border-gray-800">
          <h4 className="text-xs font-semibold text-slate-300 mb-2">
            Aggregated Daily Sentiment Score (Input to LSTM)
          </h4>
          <div className="h-44 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={daily_sentiment} margin={{ top: 5, right: 5, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1F2937" vertical={false} />
                <XAxis dataKey="date" stroke="#6B7280" fontSize={10} tickFormatter={(v) => v?.slice(5)} />
                <YAxis stroke="#6B7280" fontSize={10} domain={[-1, 1]} ticks={[-1, -0.5, 0, 0.5, 1]} />
                <Tooltip
                  content={({ active, payload, label }) => {
                    if (active && payload && payload.length) {
                      const val = payload[0].value;
                      return (
                        <div className="bg-[#0B0F19] border border-gray-700 p-2.5 rounded-lg text-xs">
                          <p className="font-semibold text-slate-200">{label}</p>
                          <p className={`font-mono font-bold mt-1 ${val >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                            Daily Sentiment: {val > 0 ? `+${val}` : val}
                          </p>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                <Bar dataKey="sentiment_score" radius={[2, 2, 0, 0]}>
                  {daily_sentiment.map((entry, index) => (
                    <Cell
                      key={`sent-cell-${index}`}
                      fill={entry.sentiment_score >= 0 ? '#10B981' : '#EF4444'}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
    </div>
  );
}
