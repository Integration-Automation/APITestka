"""Tests for the GUI environment-manager model."""
from __future__ import annotations

import json

import pytest

from je_api_testka.data.variable_store import variable_store
from je_api_testka.gui.env_manager_model import EnvManagerModel


def test_upsert_and_list():
    model = EnvManagerModel()
    model.upsert("dev", {"base": "http://dev.invalid"})
    model.upsert("prod", {"base": "http://prod.invalid"})
    names = sorted(env.name for env in model.list_envs())
    assert names == ["dev", "prod"]


def test_activate_pushes_into_variable_store():
    variable_store.clear()
    model = EnvManagerModel()
    model.upsert("dev", {"base": "http://dev.invalid"})
    model.activate("dev")
    assert model.active == "dev"
    assert variable_store.get("base") == "http://dev.invalid"
    variable_store.clear()


def test_remove_clears_active():
    model = EnvManagerModel()
    model.upsert("dev", {})
    model.activate("dev")
    model.remove("dev")
    assert model.active == ""


def test_export_and_import_roundtrip(tmp_path):
    model = EnvManagerModel()
    model.upsert("dev", {"a": "1"})
    target = tmp_path / "envs.json"
    model.export_to_file(str(target))

    loaded = EnvManagerModel()
    loaded.import_from_file(str(target))
    assert loaded.list_envs()[0].values == {"a": "1"}


def test_import_rejects_non_object(tmp_path):
    target = tmp_path / "bad.json"
    target.write_text(json.dumps([1, 2]), encoding="utf-8")
    with pytest.raises(TypeError):
        EnvManagerModel().import_from_file(str(target))
