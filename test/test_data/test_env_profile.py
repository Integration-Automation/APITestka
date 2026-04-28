"""Tests for env profile loader."""
from __future__ import annotations

import json

import pytest

from je_api_testka.data.env_profile import load_env_profile
from je_api_testka.data.variable_store import VariableStore


def test_load_env_profile_writes_into_store(tmp_path):
    store = VariableStore()
    target = tmp_path / "dev.json"
    target.write_text(json.dumps({"base_url": "http://x.invalid", "token": "t"}), encoding="utf-8")
    profile = load_env_profile(str(target), store=store)
    assert profile.name == "dev"
    assert store.get("base_url") == "http://x.invalid"
    assert store.get("token") == "t"


def test_load_env_profile_rejects_non_object(tmp_path):
    target = tmp_path / "bad.json"
    target.write_text(json.dumps([1, 2]), encoding="utf-8")
    with pytest.raises(TypeError):
        load_env_profile(str(target), store=VariableStore())
