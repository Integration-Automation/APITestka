"""
Retry helper with exponential backoff and optional jitter.
"""
from __future__ import annotations

import secrets
import time
from dataclasses import dataclass, field
from typing import Callable, Tuple, Type, TypeVar

from je_api_testka.utils.logging.loggin_instance import apitestka_logger

DEFAULT_MAX_ATTEMPTS: int = 3
DEFAULT_INITIAL_DELAY_SECONDS: float = 0.5
DEFAULT_BACKOFF_FACTOR: float = 2.0
DEFAULT_MAX_DELAY_SECONDS: float = 30.0

T = TypeVar("T")


@dataclass
class RetryPolicy:
    """Retry configuration consumed by :func:`retry_call`."""

    max_attempts: int = DEFAULT_MAX_ATTEMPTS
    initial_delay_seconds: float = DEFAULT_INITIAL_DELAY_SECONDS
    backoff_factor: float = DEFAULT_BACKOFF_FACTOR
    max_delay_seconds: float = DEFAULT_MAX_DELAY_SECONDS
    jitter: bool = True
    retry_on: Tuple[Type[BaseException], ...] = field(default_factory=lambda: (Exception,))

    def compute_delay(self, attempt: int) -> float:
        delay = self.initial_delay_seconds * (self.backoff_factor ** max(attempt - 1, 0))
        delay = min(delay, self.max_delay_seconds)
        if self.jitter:
            # SystemRandom is the OS CSPRNG; suitable for retry jitter.
            delay = delay * (0.5 + secrets.SystemRandom().random() * 0.5)  # NOSONAR S2245
        return max(delay, 0.0)


def retry_call(func: Callable[..., T], *args, policy: RetryPolicy = None, **kwargs) -> T:
    """Invoke ``func(*args, **kwargs)`` honouring ``policy``."""
    active_policy = policy or RetryPolicy()
    last_error: BaseException
    for attempt in range(1, active_policy.max_attempts + 1):
        try:
            return func(*args, **kwargs)
        except active_policy.retry_on as error:
            last_error = error
            if attempt >= active_policy.max_attempts:
                apitestka_logger.error(
                    f"retry_call exhausted after {attempt} attempts: {repr(error)}"
                )
                raise
            delay = active_policy.compute_delay(attempt)
            apitestka_logger.info(
                f"retry_call attempt {attempt} failed: {repr(error)}; sleeping {delay:.2f}s"
            )
            time.sleep(delay)
    raise last_error  # pragma: no cover - loop always returns or raises
