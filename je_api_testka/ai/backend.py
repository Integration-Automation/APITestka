"""
Pluggable AI backend.

* :class:`NoOpAIBackend` is the default - it never calls a network or LLM.
* :class:`StaticAIBackend` returns canned responses, useful for tests.
* Users plug in their own subclass via :func:`set_ai_backend`. The plumbing
  for actual Anthropic / OpenAI / local LLM calls is intentionally outside
  this package.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional


class AIBackend:
    """Strategy interface. Override :meth:`complete` in subclasses."""

    def complete(self, prompt: str, *, context: Optional[dict] = None) -> str:
        raise NotImplementedError


class NoOpAIBackend(AIBackend):
    """Default backend: returns an empty string and refuses to call out."""

    def complete(self, prompt: str, *, context: Optional[dict] = None) -> str:
        return ""


@dataclass
class StaticAIBackend(AIBackend):
    """Test-friendly backend that returns ``response`` regardless of prompt."""

    response: str = ""

    def complete(self, prompt: str, *, context: Optional[dict] = None) -> str:  # noqa: D401
        return self.response


_active_backend: AIBackend = NoOpAIBackend()


def ai_backend() -> AIBackend:
    """Return the currently registered backend."""
    return _active_backend


def set_ai_backend(backend: AIBackend) -> None:
    """Replace the active backend (e.g. install a real LLM-backed one)."""
    global _active_backend
    if not isinstance(backend, AIBackend):
        raise TypeError("backend must be an AIBackend subclass")
    _active_backend = backend
