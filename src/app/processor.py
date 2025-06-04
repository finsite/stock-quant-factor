# """Processor module for news sentiment analysis."""

from typing import Any

from textblob import TextBlob

from app.logger import setup_logger

# Initialize logger
logger = setup_logger(__name__)


def analyze_sentiment(data: dict[str, Any]) -> dict[str, Any]:
    """Analyzes sentiment of news content.
    
    Args:
    ----
        data (dict[str, Any]): A dictionary containing at least a 'headline' or 'content' key.

    :param data: dict[str:
    :param Any: param data: dict[str:
    :param Any: param data: dict[str:
    :param Any: param data:
    :param Any: param data:
    :param data: dict[str:
    :param data: dict[str:
    :param Any: param data: dict[str:
    :param Any: 
    :param data: dict[str: 
    :param Any]: 

    """
    content = data.get("headline") or data.get("content")

    if not content:
        logger.warning("No text found for sentiment analysis.")
        data["sentiment_score"] = None
        data["sentiment_label"] = "unknown"
        return data

    try:
        analysis = TextBlob(content)
        sentiment: Any = analysis.sentiment  # ✅ Avoid Pyright complaint
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
    """Classifies polarity score into sentiment label.
    
    Args:
    ----
        score (float): Polarity score from -1 to 1.

    :param score: float:
    :param score: float:
    :param score: float:
    :param score: type score: float :
    :param score: type score: float :
    :param score: float:
    :param score: float:
    :param score: float:
    :param score: float: 

    """
    if score > 0.1:
        return "positive"
    elif score < -0.1:
        return "negative"
    return "neutral"
