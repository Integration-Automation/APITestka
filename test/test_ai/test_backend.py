"""Tests for the AI backend strategy registry."""
from __future__ import annotations

import pytest

from je_api_testka.ai.backend import (
    NoOpAIBackend,
    StaticAIBackend,
    ai_backend,
    set_ai_backend,
)


def test_default_backend_is_noop():
    set_ai_backend(NoOpAIBackend())
    assert isinstance(ai_backend(), NoOpAIBackend)


def test_static_backend_returns_response():
    set_ai_backend(StaticAIBackend(response="hi"))
    assert ai_backend().complete("anything") == "hi"
    set_ai_backend(NoOpAIBackend())


def test_set_backend_rejects_non_subclass():
    with pytest.raises(TypeError):
        set_ai_backend("not a backend")  # type: ignore[arg-type]
