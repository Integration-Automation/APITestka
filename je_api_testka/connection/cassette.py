"""
VCR-style cassette: record HTTP request/response pairs to a JSON file and
replay them on subsequent runs to keep tests offline-deterministic.

The cassette stores a list of ``CassetteRecord`` keyed by (method, url, body)
so duplicate requests are de-duplicated.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional


@dataclass
class CassetteRecord:
    """One stored request/response pair."""

    method: str
    url: str
    request_body: str
    response_status: int
    response_body: str
    response_headers: Dict[str, str] = field(default_factory=dict)


def _record_key(method: str, url: str, body: str) -> str:
    raw = f"{method.upper()}|{url}|{body}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


class Cassette:
    """JSON-backed key/value store for request/response pairs."""

    def __init__(self, file_path: str) -> None:
        self.path = Path(file_path)
        self._entries: Dict[str, CassetteRecord] = {}
        if self.path.exists():
            for raw in json.loads(self.path.read_text(encoding="utf-8")):
                record = CassetteRecord(**raw)
                self._entries[_record_key(record.method, record.url, record.request_body)] = record

    def get(self, method: str, url: str, body: str = "") -> Optional[CassetteRecord]:
        return self._entries.get(_record_key(method, url, body))

    def put(self, record: CassetteRecord) -> None:
        self._entries[_record_key(record.method, record.url, record.request_body)] = record
        self._flush()

    def items(self) -> List[CassetteRecord]:
        return list(self._entries.values())

    def _flush(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = [asdict(record) for record in self._entries.values()]
        self.path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def replay_or_record(
    cassette: Cassette,
    method: str,
    url: str,
    body: str,
    perform_request: Callable[[], Any],
    extract_response: Callable[[Any], CassetteRecord],
) -> CassetteRecord:
    """Return the cassette entry if present; otherwise call the live request and store it."""
    cached = cassette.get(method, url, body)
    if cached is not None:
        return cached
    live = perform_request()
    record = extract_response(live)
    cassette.put(record)
    return record
