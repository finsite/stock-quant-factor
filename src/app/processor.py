"""Processor module for sentiment analysis of news content."""

from typing import Any, cast

from textblob import TextBlob
from textblob.sentiments import PatternAnalyzer

from app.utils.setup_logger import setup_logger

logger = setup_logger(__name__)


def analyze_sentiment(data: dict[str, Any]) -> dict[str, Any]:
    """Analyzes the sentiment of a news headline or article.

    Args:
        data (dict[str, Any]): Input data with 'headline' or 'content'.

    Returns:
        dict[str, Any]: Data enriched with sentiment_score and sentiment_label.

    """
    content = data.get("headline") or data.get("content")

    if not content:
        logger.warning("No text found for sentiment analysis.")
        data["sentiment_score"] = None
        data["sentiment_label"] = "unknown"
        return data

    try:
        analysis = TextBlob(content)
        sentiment = cast(PatternAnalyzer, analysis.analyzer).analyze(content)
        polarity = sentiment.polarity

        data["sentiment_score"] = polarity
        data["sentiment_label"] = classify_sentiment(polarity)

        logger.info("Sentiment analysis complete: %.2f (%s)", polarity, data["sentiment_label"])
        return data
    except Exception as e:
        logger.error("Sentiment analysis failed: %s", e)
        data["sentiment_score"] = None
        data["sentiment_label"] = "error"
        return data


def classify_sentiment(score: float) -> str:
    """Classifies a polarity score into a sentiment label.

    Args:
        score (float): Sentiment polarity score from -1 to 1.

    Returns:
        str: One of 'positive', 'negative', or 'neutral'.

    """
    if score > 0.1:
        return "positive"
    elif score < -0.1:
        return "negative"
    return "neutral"
