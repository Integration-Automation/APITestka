"""
OpenTelemetry hooks.

If ``opentelemetry-api`` is not installed, :func:`instrument_request` becomes a
no-op so importing this module never adds a hard dependency.
"""
from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator, Optional

from je_api_testka.utils.logging.loggin_instance import apitestka_logger

OTEL_TRACER_NAME: str = "je_api_testka"


def _try_import_tracer():
    try:
        from opentelemetry import trace  # type: ignore
        return trace.get_tracer(OTEL_TRACER_NAME)
    except ImportError:
        return None


def is_otel_available() -> bool:
    return _try_import_tracer() is not None


@contextmanager
def instrument_request(
    method: str,
    url: str,
    attributes: Optional[dict] = None,
) -> Iterator[None]:
    """Wrap a request in an OTel span if OpenTelemetry is installed."""
    tracer = _try_import_tracer()
    if tracer is None:
        apitestka_logger.debug("instrument_request: OpenTelemetry not installed; skipping span")
        yield
        return
    span_name = f"{method.upper()} {url}"
    with tracer.start_as_current_span(span_name) as span:
        span.set_attribute("http.method", method.upper())
        span.set_attribute("http.url", url)
        if attributes:
            for key, value in attributes.items():
                span.set_attribute(key, value)
        yield
