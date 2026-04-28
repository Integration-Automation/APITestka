"""
Lightweight fake-data generators (no external Faker dependency required).

For richer data sets install ``Faker`` separately and use it directly; these
helpers exist so action JSON scripts can call ``AT_fake_*`` without extra deps.
"""
from __future__ import annotations

import secrets
import string
import uuid

DEFAULT_WORD_LENGTH: int = 8
EMAIL_DOMAIN: str = "example.invalid"


def fake_uuid() -> str:
    """Return a fresh UUID4 string."""
    return str(uuid.uuid4())


def fake_word(length: int = DEFAULT_WORD_LENGTH) -> str:
    """Return a random lowercase word of ``length`` characters."""
    # secrets.SystemRandom is the OS CSPRNG; safe for token-shaped fake data.
    rng = secrets.SystemRandom()  # NOSONAR S2245
    return "".join(rng.choice(string.ascii_lowercase) for _ in range(max(length, 1)))


def fake_email(domain: str = EMAIL_DOMAIN) -> str:
    """Return ``<random-word>@<domain>``."""
    return f"{fake_word()}@{domain}"
