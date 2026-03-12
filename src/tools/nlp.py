"""NLP tools for sentiment analysis and text summarization."""
from __future__ import annotations

import os
from typing import Optional

_SENTIMENT_MODEL = None
_SENTIMENT_TOKENIZER = None
_SUMMARIZER = None
_SENTIMENT_UNAVAILABLE = False
_SUMMARIZER_UNAVAILABLE = False


def _load_sentiment_model():
    """Lazy load RoBERTa sentiment model."""
    global _SENTIMENT_MODEL, _SENTIMENT_TOKENIZER, _SENTIMENT_UNAVAILABLE
    if _SENTIMENT_UNAVAILABLE:
        return None, None
    if _SENTIMENT_MODEL is None:
        try:
            from transformers import AutoTokenizer, AutoModelForSequenceClassification
            model_name = "cardiffnlp/twitter-roberta-base-sentiment-latest"
            _SENTIMENT_TOKENIZER = AutoTokenizer.from_pretrained(model_name)
            _SENTIMENT_MODEL = AutoModelForSequenceClassification.from_pretrained(model_name)
        except Exception as e:
            print(f"Warning: Could not load sentiment model: {e}")
            _SENTIMENT_UNAVAILABLE = True
            return None, None
    return _SENTIMENT_MODEL, _SENTIMENT_TOKENIZER


def _load_summarizer():
    """Lazy load BART summarization model."""
    global _SUMMARIZER, _SUMMARIZER_UNAVAILABLE
    if _SUMMARIZER_UNAVAILABLE:
        return None
    if _SUMMARIZER is None:
        try:
            from transformers import pipeline
            _SUMMARIZER = pipeline("summarization", model="facebook/bart-large-cnn")
        except Exception as e:
            print(f"Warning: Could not load summarizer: {e}")
            _SUMMARIZER_UNAVAILABLE = True
            return None
    return _SUMMARIZER


def analyze_sentiment(text: str) -> dict:
    """
    Analyze sentiment of text using RoBERTa.
    
    Returns:
        dict with keys: sentiment (negative/neutral/positive), 
        scores (dict with all three scores), confidence (float)
    """
    if not text or not text.strip():
        return {"sentiment": "neutral", "confidence": 0.0, "scores": {}}
    
    model, tokenizer = _load_sentiment_model()
    if model is None or tokenizer is None:
        return {"error": "sentiment_model_unavailable", "sentiment": "unknown", "confidence": 0.0}
    
    try:
        import torch
        
        # Tokenize and predict
        inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        with torch.no_grad():
            outputs = model(**inputs)
        
        # Get probabilities
        scores = torch.nn.functional.softmax(outputs.logits, dim=1)[0]
        labels = ["negative", "neutral", "positive"]
        
        scores_dict = {label: float(score) for label, score in zip(labels, scores)}
        sentiment = labels[scores.argmax().item()]
        confidence = float(scores.max().item())
        
        return {
            "sentiment": sentiment,
            "confidence": confidence,
            "scores": scores_dict
        }
    except Exception as e:
        return {"error": str(e), "sentiment": "unknown", "confidence": 0.0}


def analyze_batch_sentiment(texts: list[str]) -> list[dict]:
    """Analyze sentiment for multiple texts."""
    return [analyze_sentiment(text) for text in texts]


def summarize_text(text: str, max_length: int = 130, min_length: int = 30) -> dict:
    """
    Summarize text using BART.
    
    Returns:
        dict with keys: summary (str), original_length (int), summary_length (int)
    """
    if not text or not text.strip():
        return {"summary": "", "original_length": 0, "summary_length": 0}
    
    # Skip summarization for very short texts
    if len(text.split()) < min_length:
        return {
            "summary": text,
            "original_length": len(text.split()),
            "summary_length": len(text.split()),
            "note": "Text too short to summarize"
        }
    
    summarizer = _load_summarizer()
    if summarizer is None:
        return {"error": "summarizer_unavailable", "summary": text[:200] + "..."}
    
    try:
        result = summarizer(text, max_length=max_length, min_length=min_length, do_sample=False)
        summary = result[0]['summary_text']
        
        return {
            "summary": summary,
            "original_length": len(text.split()),
            "summary_length": len(summary.split()),
            "compression_ratio": round(len(summary.split()) / len(text.split()), 2)
        }
    except Exception as e:
        return {"error": str(e), "summary": text[:200] + "..."}


def extract_key_phrases(text: str, top_n: int = 5) -> list[str]:
    """
    Extract key phrases from text using simple frequency analysis.
    This is a lightweight alternative when full NLP models aren't available.
    """
    if not text:
        return []
    
    try:
        from collections import Counter
        import re
        
        # Simple tokenization
        words = re.findall(r'\b[a-z]{4,}\b', text.lower())
        
        # Remove common stop words
        stop_words = {'that', 'this', 'with', 'from', 'have', 'been', 'were', 'will', 'would', 'could', 'should'}
        words = [w for w in words if w not in stop_words]
        
        # Get most common
        counter = Counter(words)
        return [word for word, _ in counter.most_common(top_n)]
    except Exception:
        return []
