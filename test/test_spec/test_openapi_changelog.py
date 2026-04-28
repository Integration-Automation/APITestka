"""Tests for the openapi_changelog markdown."""
from __future__ import annotations

from je_api_testka.spec.openapi_changelog import openapi_changelog


def test_no_changes_message():
    spec = {"paths": {"/x": {"get": {"responses": {"200": {}}}}}}
    out = openapi_changelog(spec, spec)
    assert "No changes" in out


def test_added_path_appears_in_changelog():
    left = {"paths": {}}
    right = {"paths": {"/x": {"get": {"responses": {"200": {}}}}}}
    out = openapi_changelog(left, right)
    assert "Added paths" in out
    assert "/x" in out


def test_schema_change_section_listed():
    left = {"paths": {"/x": {"get": {"responses": {"200": {"description": "old"}}}}}}
    right = {"paths": {"/x": {"get": {"responses": {"200": {"description": "new"}}}}}}
    out = openapi_changelog(left, right)
    assert "Schema changes" in out
