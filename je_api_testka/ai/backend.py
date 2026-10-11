"""
Pluggable AI backend.

* :class:`NoOpAIBackend` is the default - it never calls a network or LLM, and
  every AI helper then uses its deterministic fallback.
* :class:`StaticAIBackend` returns canned responses, useful for tests.
* :class:`~je_api_testka.ai.anthropic_backend.AnthropicAIBackend` is the
  reference implementation on the Anthropic API (``ai`` extra).
* Users plug in their own subclass via :func:`set_ai_backend`.

A backend answers with plain text; an empty string means "no answer", and the
callers then fall back to their deterministic behaviour.

Selection: :func:`set_ai_backend` or :func:`select_ai_backend` (also the
``AT_select_ai_backend`` command). When neither was called, the first
:func:`ai_backend` call reads ``APITESTKA_AI_BACKEND`` (``noop`` or
``anthropic``; ``APITESTKA_AI_MODEL`` and ``APITESTKA_AI_EFFORT`` tune the
Anthropic backend), so the CLI, the MCP server and the socket server can use a
real model without code changes.
"""
from __future__ import annotations

import os
import threading
from dataclasses import dataclass
from typing import Dict, Optional

from je_api_testka.utils.exception.exceptions import APIAIBackendException

AI_BACKEND_ENV: str = "APITESTKA_AI_BACKEND"
AI_MODEL_ENV: str = "APITESTKA_AI_MODEL"
AI_EFFORT_ENV: str = "APITESTKA_AI_EFFORT"
NOOP_BACKEND: str = "noop"
ANTHROPIC_BACKEND: str = "anthropic"
BACKEND_NAMES = (NOOP_BACKEND, ANTHROPIC_BACKEND)


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


# The active backend; empty until set or first read from the environment.
_selection: Dict[str, AIBackend] = {}
_lock = threading.Lock()
_ACTIVE: str = "active"


def build_ai_backend(name: str = NOOP_BACKEND, model: Optional[str] = None,
                     effort: Optional[str] = None) -> AIBackend:
    """
    Return a new backend by name: ``noop`` or ``anthropic``.

    ``model`` and ``effort`` apply to the Anthropic backend (its defaults when ``None``).

    :raises APIAIBackendException: for an unknown name, or options given to ``noop``.
    """
    if name == NOOP_BACKEND:
        if model or effort:
            raise APIAIBackendException("the noop AI backend takes no model or effort")
        return NoOpAIBackend()
    if name == ANTHROPIC_BACKEND:
        from je_api_testka.ai.anthropic_backend import AnthropicAIBackend  # the module imports this one
        options = {key: value for key, value in (("model", model), ("effort", effort)) if value}
        return AnthropicAIBackend(**options)
    raise APIAIBackendException(f"unknown AI backend {name!r}; expected one of {BACKEND_NAMES}")


def _backend_from_environment() -> AIBackend:
    name = os.environ.get(AI_BACKEND_ENV, "").strip().lower() or NOOP_BACKEND
    if name == NOOP_BACKEND:
        return NoOpAIBackend()
    return build_ai_backend(name, model=os.environ.get(AI_MODEL_ENV) or None,
                            effort=os.environ.get(AI_EFFORT_ENV) or None)


def ai_backend() -> AIBackend:
    """Return the active backend; on first use without a selection, build it from the environment."""
    with _lock:
        if _ACTIVE not in _selection:
            _selection[_ACTIVE] = _backend_from_environment()
        return _selection[_ACTIVE]


def set_ai_backend(backend: AIBackend) -> None:
    """Replace the active backend (e.g. install a real LLM-backed one)."""
    if not isinstance(backend, AIBackend):
        raise TypeError("backend must be an AIBackend subclass")
    with _lock:
        _selection[_ACTIVE] = backend


def select_ai_backend(name: str = NOOP_BACKEND, model: Optional[str] = None,
                      effort: Optional[str] = None) -> str:
    """Build a backend with :func:`build_ai_backend`, make it active and return its class name."""
    backend = build_ai_backend(name, model=model, effort=effort)
    set_ai_backend(backend)
    return type(backend).__name__
