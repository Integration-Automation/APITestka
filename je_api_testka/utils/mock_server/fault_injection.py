"""
Fault injection helpers for the Flask mock server.

* :class:`FaultInjector` lets a test harness flip global latency or error
  injection on/off without touching every route.
* The instance is wrapped through :meth:`wrap` to apply the configured faults
  to any Flask view function.
"""
from __future__ import annotations

import secrets
import time
from dataclasses import dataclass
from typing import Callable, Optional

from flask import Response

from je_api_testka.utils.logging.loggin_instance import apitestka_logger

DEFAULT_FAILURE_STATUS: int = 500
MIN_PROBABILITY: float = 0.0
MAX_PROBABILITY: float = 1.0


@dataclass
class FaultInjector:
    """Centralised toggles for latency and synthetic error responses."""

    latency_seconds: float = 0.0
    failure_probability: float = 0.0
    failure_status: int = DEFAULT_FAILURE_STATUS
    failure_body: str = "injected failure"

    def __post_init__(self) -> None:
        self._validate_probability(self.failure_probability)

    def _validate_probability(self, value: float) -> None:
        if not MIN_PROBABILITY <= value <= MAX_PROBABILITY:
            raise ValueError(f"failure_probability must be in [0, 1], got {value}")

    def configure(self, *, latency_seconds: Optional[float] = None,
                  failure_probability: Optional[float] = None,
                  failure_status: Optional[int] = None,
                  failure_body: Optional[str] = None) -> None:
        if latency_seconds is not None:
            self.latency_seconds = max(latency_seconds, 0.0)
        if failure_probability is not None:
            self._validate_probability(failure_probability)
            self.failure_probability = failure_probability
        if failure_status is not None:
            self.failure_status = failure_status
        if failure_body is not None:
            self.failure_body = failure_body

    def wrap(self, view: Callable[..., Response]) -> Callable[..., Response]:
        """Decorate a Flask view with the configured latency / failure rules."""

        def _wrapped(*args, **kwargs):
            if self.latency_seconds > 0:
                time.sleep(self.latency_seconds)
            if self.failure_probability > 0:
                roll = secrets.SystemRandom().random()
                if roll < self.failure_probability:
                    apitestka_logger.info(
                        f"FaultInjector triggered failure (roll={roll:.3f})"
                    )
                    return Response(self.failure_body, status=self.failure_status)
            return view(*args, **kwargs)

        _wrapped.__name__ = getattr(view, "__name__", "fault_wrapped_view")
        return _wrapped
