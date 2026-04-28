"""Tests for the VCR-style cassette."""
from __future__ import annotations

from je_api_testka.connection.cassette import Cassette, CassetteRecord, replay_or_record


def test_put_and_get_roundtrip(tmp_path):
    cassette = Cassette(str(tmp_path / "data.json"))
    cassette.put(CassetteRecord(
        method="GET", url="http://x.invalid", request_body="",
        response_status=200, response_body="ok", response_headers={"X-Test": "1"},
    ))
    fetched = cassette.get("GET", "http://x.invalid")
    assert fetched is not None
    assert fetched.response_body == "ok"
    assert fetched.response_headers == {"X-Test": "1"}


def test_persisted_cassette_reloads_from_disk(tmp_path):
    path = tmp_path / "data.json"
    first = Cassette(str(path))
    first.put(CassetteRecord(
        method="POST", url="http://x.invalid/api", request_body='{"a":1}',
        response_status=201, response_body='{"id": 7}',
    ))
    second = Cassette(str(path))
    assert second.get("POST", "http://x.invalid/api", body='{"a":1}').response_status == 201


def test_replay_or_record_uses_cache_on_second_call(tmp_path):
    cassette = Cassette(str(tmp_path / "data.json"))
    counter = {"calls": 0}

    def _live():
        counter["calls"] += 1
        return {"status": 200, "body": "ok"}

    def _extract(_resp):
        return CassetteRecord(
            method="GET", url="http://x.invalid", request_body="",
            response_status=200, response_body="ok",
        )

    replay_or_record(cassette, "GET", "http://x.invalid", "", _live, _extract)
    replay_or_record(cassette, "GET", "http://x.invalid", "", _live, _extract)
    assert counter["calls"] == 1


def test_executor_cassette_lookup_returns_empty_when_missing(tmp_path):
    from je_api_testka.utils.executor.action_executor import execute_action

    record = execute_action([
        ["AT_cassette_lookup", {
            "file_path": str(tmp_path / "missing.json"),
            "method": "GET",
            "url": "http://x.invalid",
        }],
    ])
    assert next(iter(record.values())) == {}
