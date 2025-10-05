import logging
from collections.abc import MutableMapping, Mapping
from functools import lru_cache
from typing import Any

import orjson
import structlog
from structlog_sentry import SentryProcessor


def add_loki_labels(
    logger: Any, method_name: str, event_dict: MutableMapping[str, Any]
) -> Mapping[str, Any]:
    event_dict["app"] = "expenses-tracker"
    event_dict["service"] = "api"
    return event_dict


@lru_cache(maxsize=1)
def prepare_logger(log_level: str = "INFO") -> None:
    structlog.configure(
        cache_logger_on_first_use=True,
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        processors=[
            structlog.processors.add_log_level,
            structlog.processors.format_exc_info,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            add_loki_labels,
            SentryProcessor(level=logging.WARNING),
            structlog.processors.JSONRenderer(serializer=orjson.dumps),
        ],
        logger_factory=structlog.BytesLoggerFactory(),
    )
