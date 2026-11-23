"""
LangSmith tracing setup.

pydantic-settings reads the .env file into `settings`, but it does NOT put
the values into os.environ. LangChain / LangSmith only look at os.environ, so
the values have to be exported here. This must run before the first traced
call, because LangSmith caches the environment lookups.
"""

import logging
import os

from backend.app.core.config import settings

logger = logging.getLogger(__name__)


def setup_tracing() -> bool:
    """Export LangSmith settings to the environment. Returns True if tracing is on."""

    enabled = settings.LANGSMITH_TRACING and bool(settings.LANGSMITH_API_KEY)

    if not enabled:
        for name in ("LANGSMITH_TRACING", "LANGCHAIN_TRACING_V2"):
            os.environ[name] = "false"

        if settings.LANGSMITH_TRACING:
            logger.warning(
                "LANGSMITH_TRACING=true but LANGSMITH_API_KEY is empty; "
                "tracing stays off."
            )

        return False

    values = {
        "LANGSMITH_TRACING": "true",
        "LANGSMITH_API_KEY": settings.LANGSMITH_API_KEY,
        "LANGSMITH_PROJECT": settings.LANGSMITH_PROJECT,
        "LANGSMITH_HIDE_INPUTS": str(settings.LANGSMITH_HIDE_INPUTS).lower(),
        "LANGSMITH_HIDE_OUTPUTS": str(settings.LANGSMITH_HIDE_OUTPUTS).lower(),
        # Older langchain versions still read the LANGCHAIN_* names.
        "LANGCHAIN_TRACING_V2": "true",
        "LANGCHAIN_API_KEY": settings.LANGSMITH_API_KEY,
        "LANGCHAIN_PROJECT": settings.LANGSMITH_PROJECT,
    }

    if settings.LANGSMITH_ENDPOINT:
        values["LANGSMITH_ENDPOINT"] = settings.LANGSMITH_ENDPOINT
        values["LANGCHAIN_ENDPOINT"] = settings.LANGSMITH_ENDPOINT

    os.environ.update(values)

    logger.info(
        "LangSmith tracing enabled (project=%s, hide_inputs=%s)",
        settings.LANGSMITH_PROJECT,
        settings.LANGSMITH_HIDE_INPUTS,
    )

    return True
