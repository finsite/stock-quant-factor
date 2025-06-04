"""Main entry point for the stock-quant-factor module.

Initializes the factor-based strategy service, sets up logging,
and begins consuming data for factor signal generation.
"""

import os
import sys

# Add 'src/' to Python's module search path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.logger import setup_logger
from app.queue_handler import consume_messages

# Initialize logger
logger = setup_logger(__name__)


def main() -> None:
    """Starts the factor strategy service.
    
    This service consumes upstream market/fundamental data, computes factor scores,
    and emits ranked signals for downstream use.


    
    """
    logger.info("🚀 Starting Factor Strategy Service...")
    consume_messages()


if __name__ == "__main__":
    main()
