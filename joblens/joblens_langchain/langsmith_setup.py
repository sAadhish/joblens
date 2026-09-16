# ===================================
# LANGSMITH SETUP
# Call this at the start of main.py
# Enables tracing for all LangChain calls
# ===================================

import os
from config import Config
from logger import logger


def setup_langsmith():
    """
    Configures LangSmith tracing.
    
    Why set env vars explicitly here rather than relying on .env?
    LangChain reads these specific env var names at import time.
    Setting them programmatically ensures they're set before
    any LangChain component initializes.
    """
    if not Config.LANGCHAIN_API_KEY:
        logger.warning("LANGCHAIN_API_KEY not set — LangSmith tracing disabled")
        return False

    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_API_KEY"] = Config.LANGCHAIN_API_KEY
    os.environ["LANGCHAIN_PROJECT"] = Config.LANGCHAIN_PROJECT
    os.environ["LANGCHAIN_ENDPOINT"] = Config.LANGCHAIN_ENDPOINT

    logger.info(f"LangSmith tracing enabled — project: {Config.LANGCHAIN_PROJECT}")
    return True