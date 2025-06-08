"""Factor scoring engine for stock-quant-factor.

This module evaluates instruments using multi-factor models such as
value, momentum, and quality. It computes a composite score and returns
a signal if the score exceeds the configured threshold.
"""

from typing import Any

from app.config import get_factor_model, get_signal_threshold
from app.utils.setup_logger import setup_logger

logger = setup_logger(__name__)


def run_factor_analysis(payload: dict[str, Any]) -> dict[str, Any] | None:
    """Processes an instrument's factor inputs and calculates a composite score.

    Args:
    ----
        payload (dict[str, Any]): Incoming data including:
            - symbol (str): Instrument identifier
            - timestamp (str): ISO-8601 timestamp
            - factors (dict[str, float]): Scores for each factor (e.g., value, momentum, quality)

    Returns:
    -------
        dict[str, Any] | None: A signal dict if the score exceeds threshold, else None.
    """
    symbol = payload.get("symbol")
    timestamp = payload.get("timestamp")
    factors = payload.get("factors", {})  # e.g., {"value": 0.8, "momentum": 0.6, "quality": 0.9}

    if not factors or not symbol:
        logger.warning("❌ Missing required factor data or symbol.")
        return None

    model = get_factor_model()
    threshold = get_signal_threshold()

    logger.debug(f"📊 Using factor model: {model}, Threshold: {threshold}")

    # Simple average for now — extendable to weighted model
    score = sum(factors.values()) / len(factors)

    logger.debug(f"📈 {symbol} factor score: {score:.4f}")

    if score >= threshold:
        logger.info(f"✅ Factor signal detected for {symbol} with score {score:.4f}")
        return {
            "type": "factor_signal",
            "symbol": symbol,
            "score": round(score, 4),
            "model": model,
            "timestamp": timestamp,
            "confidence": "high" if score > 0.9 else "moderate",
        }

    return None
