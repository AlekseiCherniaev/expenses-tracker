import logging

import sentry_sdk
import structlog
from fastapi import HTTPException
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.types import Event, Hint

from expenses_tracker.core.constants import Environment
from expenses_tracker.core.settings import Settings

logger = structlog.get_logger(__name__)


def before_send(event: Event, hint: Hint) -> Event | None:
    if "exc_info" in hint:
        _, exc_value, _ = hint["exc_info"]
        if isinstance(exc_value, HTTPException) and exc_value.status_code < 500:
            return None
    return event


def init_sentry(settings: Settings) -> None:
    if not settings.sentry_dsn:
        return
    is_prod = settings.environment == Environment.PROD

    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        environment=settings.environment.value.lower(),
        release=settings.project_version,
        integrations=[
            FastApiIntegration(),
            SqlalchemyIntegration(),
            RedisIntegration(),
            LoggingIntegration(event_level=logging.WARNING),
        ],
        traces_sample_rate=settings.sentry_traces_sample_rate,
        profiles_sample_rate=settings.sentry_profiles_sample_rate,
        before_send=before_send,
        send_default_pii=not is_prod,
    )
    logger.info("Sentry initialized")
