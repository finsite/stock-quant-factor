"""Repo-specific configuration for stock-quant-factor."""

from app.config_shared import *


def get_poller_name() -> str:
    """Return the name of the poller for this service."""
    return get_config_value("POLLER_NAME", "stock_quant_factor")


def get_rabbitmq_queue() -> str:
    """Return the RabbitMQ queue name for this poller."""
    return get_config_value("RABBITMQ_QUEUE", "stock_quant_factor_queue")


def get_dlq_name() -> str:
    """Return the Dead Letter Queue (DLQ) name for this poller."""
    return get_config_value("DLQ_NAME", "stock_quant_factor_dlq")

def get_factor_model() -> str:
    """Return the factor model to use (e.g., 'fama_french')."""
    return get_config_value("FACTOR_MODEL", "fama_french")


def get_signal_threshold() -> float:
    """Return the signal threshold for factor-based decisions."""
    return float(get_config_value("SIGNAL_THRESHOLD", 0.75))