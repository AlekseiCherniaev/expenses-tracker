import logging
from functools import lru_cache

import orjson
import structlog
from structlog_sentry import SentryProcessor


@lru_cache(maxsize=1)
def prepare_logger(log_level: str = "INFO") -> None:
    structlog.configure(
        cache_logger_on_first_use=True,
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        processors=[
            structlog.processors.add_log_level,
            structlog.processors.format_exc_info,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            SentryProcessor(level=logging.WARNING),
            structlog.processors.JSONRenderer(serializer=orjson.dumps),
        ],
        logger_factory=structlog.BytesLoggerFactory(),
    )
