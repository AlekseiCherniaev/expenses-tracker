import structlog
from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.instrumentation.psycopg import PsycopgInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Tracer
from sqlalchemy.ext.asyncio import AsyncEngine

from expenses_tracker.core.settings import get_settings

logger = structlog.get_logger(__name__)


def setup_opentelemetry(app: FastAPI, engine: AsyncEngine) -> TracerProvider | None:
    if not get_settings().otel_enabled:
        logger.info("OpenTelemetry instrumentation is disabled")
        return None

    logger.info("Initializing OpenTelemetry instrumentation")

    resource = Resource.create(
        {
            SERVICE_NAME: get_settings().otel_service_name,
            SERVICE_VERSION: get_settings().project_version,
        }
    )

    tracer_provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(tracer_provider)

    otlp_exporter = OTLPSpanExporter(
        endpoint=f"{get_settings().otel_endpoint}/v1/traces",
    )

    span_processor = BatchSpanProcessor(otlp_exporter)
    tracer_provider.add_span_processor(span_processor)

    FastAPIInstrumentor.instrument_app(app, tracer_provider=tracer_provider)

    SQLAlchemyInstrumentor().instrument(engine=engine.sync_engine)
    PsycopgInstrumentor().instrument()

    RedisInstrumentor().instrument()
    LoggingInstrumentor().instrument()

    logger.info("OpenTelemetry instrumentation completed successfully")
    return tracer_provider


def get_tracer(name: str) -> Tracer:
    return trace.get_tracer(name)
