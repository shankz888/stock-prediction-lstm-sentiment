import React from 'react';
import { Newspaper, ExternalLink, Calendar, Building2 } from 'lucide-react';

export default function NewsList({ articles, ticker }) {
  if (!articles || articles.length === 0) {
    return (
      <div className="bg-[#111827] border border-gray-800 rounded-2xl p-6 text-center text-slate-400">
        No recent news retrieved for {ticker}.
      </div>
    );
  }

  const getSentimentBadge = (sentiment, score) => {
    switch (sentiment) {
      case 'Positive':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
            Positive <span className="text-[10px] opacity-80">({(score * 100).toFixed(0)}%)</span>
          </span>
        );
      case 'Negative':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-rose-500/15 text-rose-400 border border-rose-500/30">
            Negative <span className="text-[10px] opacity-80">({(score * 100).toFixed(0)}%)</span>
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-slate-500/15 text-slate-300 border border-slate-500/30">
            Neutral <span className="text-[10px] opacity-80">({(score * 100).toFixed(0)}%)</span>
          </span>
        );
    }
  };

  return (
    <div className="bg-[#111827] border border-gray-800 rounded-2xl p-5 shadow-xl">
      {/* Header */}
      <div className="flex items-center justify-between pb-3 border-b border-gray-800 mb-4">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-lg bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
            <Newspaper className="h-4 w-4" />
          </div>
          <div>
            <h3 className="font-bold text-white text-base">Recent Financial News Feed</h3>
            <p className="text-xs text-slate-400">Classified by FinBERT Financial Sentiment Engine</p>
          </div>
        </div>

        <span className="text-xs font-mono text-slate-400 bg-gray-800/80 px-2 py-0.5 rounded border border-gray-700">
          {articles.length} Articles
        </span>
      </div>

      {/* Articles List */}
      <div className="space-y-3 max-h-[460px] overflow-y-auto pr-1">
        {articles.map((art, idx) => (
          <div
            key={idx}
            className="p-3.5 rounded-xl bg-[#162035]/60 hover:bg-[#162035] border border-gray-800 hover:border-gray-700 transition"
          >
            <div className="flex items-start justify-between gap-3">
              <h4 className="text-sm font-semibold text-slate-100 hover:text-blue-400 transition leading-snug">
                {art.headline}
              </h4>
              <div className="shrink-0">
                {getSentimentBadge(art.sentiment, art.sentiment_score || 0.5)}
              </div>
            </div>

            {art.description && (
              <p className="text-xs text-slate-400 mt-1.5 line-clamp-2 leading-relaxed">
                {art.description}
              </p>
            )}

            <div className="flex items-center justify-between mt-3 pt-2 border-t border-gray-800/60 text-[11px] text-slate-400">
              <div className="flex items-center gap-3">
                <span className="flex items-center gap-1 font-medium text-slate-300">
                  <Building2 className="h-3 w-3 text-blue-400" /> {art.source || 'Financial News'}
                </span>
                <span className="flex items-center gap-1">
                  <Calendar className="h-3 w-3 text-slate-500" /> {art.published_at}
                </span>
              </div>

              {art.url ? (
                <a
                  href={art.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-1 text-blue-400 hover:text-blue-300 font-medium transition"
                >
                  Read More <ExternalLink className="h-3 w-3" />
                </a>
              ) : (
                <span className="text-slate-600">Feed Item</span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
