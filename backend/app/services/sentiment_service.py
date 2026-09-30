import re
from typing import List, Dict, Any, Tuple
import numpy as np
import pandas as pd
from collections import defaultdict
from sqlalchemy.orm import Session

from backend.app.config import settings
from backend.app.models.schema import NewsArticle

# FinBERT pipeline holder (lazy loaded to save memory and startup time)
_finbert_pipeline = None
_finbert_load_failed = False

def get_finbert_pipeline():
    """Lazily load the Hugging Face FinBERT pipeline."""
    global _finbert_pipeline, _finbert_load_failed
    if _finbert_pipeline is not None:
        return _finbert_pipeline
    if _finbert_load_failed:
        return None

    try:
        from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
        model_name = settings.FINBERT_MODEL
        print(f"Loading FinBERT model: {model_name}...")
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSequenceClassification.from_pretrained(model_name)
        _finbert_pipeline = pipeline("text-classification", model=model, tokenizer=tokenizer)
        print("FinBERT model loaded successfully.")
        return _finbert_pipeline
    except Exception as e:
        print(f"Could not load Hugging Face FinBERT: {e}. Using financial NLP sentiment fallback.")
        _finbert_load_failed = True
        return None

# High-accuracy financial domain sentiment lexicon for fallback
FINANCIAL_POSITIVE_TERMS = {
    "growth", "profit", "surge", "gain", "dividend", "outperform", "bullish", "record",
    "expansion", "beat", "rally", "upgrade", "higher", "rebound", "strong", "positive",
    "exceed", "revenue", "innovative", "momentum", "boost", "upside", "win", "partnership"
}

FINANCIAL_NEGATIVE_TERMS = {
    "loss", "drop", "fall", "decline", "slump", "bearish", "downgrade", "debt", "crisis",
    "penalty", "investigation", "lawsuit", "layoff", "recession", "missed", "weak",
    "inflation", "risk", "warning", "underperform", "deficit", "tumble", "crash", "plunge"
}

def analyze_sentiment_lexicon(text: str) -> Tuple[str, float]:
    """
    Financial sentiment classification fallback based on domain vocabulary.
    Returns (label, confidence_score).
    """
    words = set(re.findall(r'\b[a-z]+\b', text.lower()))
    pos_count = len(words.intersection(FINANCIAL_POSITIVE_TERMS))
    neg_count = len(words.intersection(FINANCIAL_NEGATIVE_TERMS))

    if pos_count > neg_count:
        confidence = min(0.65 + (pos_count - neg_count) * 0.1, 0.95)
        return "Positive", round(confidence, 2)
    elif neg_count > pos_count:
        confidence = min(0.65 + (neg_count - pos_count) * 0.1, 0.95)
        return "Negative", round(confidence, 2)
    else:
        return "Neutral", 0.60

def analyze_article_sentiment(headline: str, description: str = "") -> Tuple[str, float]:
    """
    Analyze sentiment of a single financial news article using FinBERT or financial fallback.
    Returns: (sentiment_category, confidence_score) where sentiment is Positive/Neutral/Negative.
    """
    combined_text = f"{headline}. {description}".strip()
    if not combined_text:
        return "Neutral", 0.50

    pipe = get_finbert_pipeline()
    if pipe is not None:
        try:
            # FinBERT expects text truncated to 512 tokens
            result = pipe(combined_text[:512])[0]
            raw_label = result["label"].lower()
            score = float(result["score"])

            if "pos" in raw_label:
                return "Positive", round(score, 2)
            elif "neg" in raw_label:
                return "Negative", round(score, 2)
            else:
                return "Neutral", round(score, 2)
        except Exception as e:
            print(f"Inference error in FinBERT: {e}")

    # Fallback
    return analyze_sentiment_lexicon(combined_text)

def process_and_score_news(articles: List[Dict[str, Any]], db: Session = None) -> List[Dict[str, Any]]:
    """
    Run sentiment analysis for all articles and optionally persist to database.
    """
    processed = []
    for art in articles:
        sentiment, score = analyze_article_sentiment(
            art.get("headline", ""),
            art.get("description", "")
        )
        art_copy = dict(art)
        art_copy["sentiment"] = sentiment
        art_copy["sentiment_score"] = score
        processed.append(art_copy)

        if db is not None:
            try:
                existing = db.query(NewsArticle).filter_by(
                    ticker=art.get("ticker"),
                    headline=art.get("headline")
                ).first()
                if not existing:
                    db_art = NewsArticle(
                        ticker=art.get("ticker"),
                        headline=art.get("headline"),
                        description=art.get("description"),
                        source=art.get("source"),
                        published_at=art.get("published_at"),
                        url=art.get("url"),
                        sentiment=sentiment,
                        sentiment_score=score
                    )
                    db.add(db_art)
            except Exception as e:
                db.rollback()

    if db is not None:
        try:
            db.commit()
        except Exception:
            db.rollback()

    return processed

def aggregate_daily_sentiment(articles: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    Aggregate article sentiment by publication date.
    Returns dict: date -> {
        sentiment_score: float in [-1.0, 1.0],
        article_count: int,
        positive_count: int,
        neutral_count: int,
        negative_count: int
    }
    """
    daily_groups = defaultdict(list)
    for art in articles:
        pub_date = art.get("published_at", "")[:10]
        if not pub_date:
            continue
        sentiment = art.get("sentiment", "Neutral")
        score = art.get("sentiment_score", 0.5)

        # Convert to polarity value [-1.0, +1.0]
        if sentiment == "Positive":
            polarity = score
        elif sentiment == "Negative":
            polarity = -score
        else:
            polarity = 0.0

        daily_groups[pub_date].append((polarity, sentiment))

    results = {}
    for dt, items in daily_groups.items():
        polarities = [p[0] for p in items]
        sentiments = [p[1] for p in items]
        results[dt] = {
            "sentiment_score": round(float(np.mean(polarities)), 3),
            "article_count": len(items),
            "positive_count": sentiments.count("Positive"),
            "neutral_count": sentiments.count("Neutral"),
            "negative_count": sentiments.count("Negative"),
        }
    return results

def get_sentiment_overview(ticker: str, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Compute comprehensive sentiment metrics (PRD Section 28).
    """
    total = len(articles)
    if total == 0:
        return {
            "ticker": ticker,
            "total_articles": 0,
            "positive_count": 0,
            "neutral_count": 0,
            "negative_count": 0,
            "positive_pct": 0.0,
            "neutral_pct": 0.0,
            "negative_pct": 0.0,
            "average_score": 0.0,
            "daily_sentiment": [],
            "articles": []
        }

    pos = sum(1 for a in articles if a.get("sentiment") == "Positive")
    neu = sum(1 for a in articles if a.get("sentiment") == "Neutral")
    neg = sum(1 for a in articles if a.get("sentiment") == "Negative")

    daily_agg = aggregate_daily_sentiment(articles)
    daily_list = [
        {
            "date": dt,
            "sentiment_score": data["sentiment_score"],
            "article_count": data["article_count"],
            "positive_count": data["positive_count"],
            "neutral_count": data["neutral_count"],
            "negative_count": data["negative_count"]
        }
        for dt, data in sorted(daily_agg.items())
    ]

    all_polarities = []
    for a in articles:
        sent = a.get("sentiment")
        sc = a.get("sentiment_score", 0.5)
        if sent == "Positive":
            all_polarities.append(sc)
        elif sent == "Negative":
            all_polarities.append(-sc)
        else:
            all_polarities.append(0.0)

    avg_score = round(float(np.mean(all_polarities)), 3) if all_polarities else 0.0

    return {
        "ticker": ticker,
        "total_articles": total,
        "positive_count": pos,
        "neutral_count": neu,
        "negative_count": neg,
        "positive_pct": round(pos / total * 100, 1),
        "neutral_pct": round(neu / total * 100, 1),
        "negative_pct": round(neg / total * 100, 1),
        "average_score": avg_score,
        "daily_sentiment": daily_list,
        "articles": articles
    }
