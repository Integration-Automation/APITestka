"""
Lightweight snapshot testing helper.

Snapshots are JSON files. The first call writes the snapshot; subsequent calls
compare against it. Set ``update=True`` to overwrite. Volatile fields (such as
timestamps) can be filtered via ``ignore_keys``.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable, Optional

from je_api_testka.utils.exception.exceptions import APIAssertException
from je_api_testka.utils.logging.loggin_instance import apitestka_logger

DEFAULT_SNAPSHOT_DIR: str = "__snapshots__"


def _strip_keys(payload: Any, ignore_keys: Iterable[str]) -> Any:
    drop = set(ignore_keys)
    if isinstance(payload, dict):
        return {key: _strip_keys(value, drop) for key, value in payload.items() if key not in drop}
    if isinstance(payload, list):
        return [_strip_keys(item, drop) for item in payload]
    return payload


def assert_snapshot(
    name: str,
    payload: Any,
    snapshot_dir: Optional[str] = None,
    ignore_keys: Optional[Iterable[str]] = None,
    update: bool = False,
) -> None:
    """Compare ``payload`` against the snapshot file ``<snapshot_dir>/<name>.json``."""
    apitestka_logger.info(f"snapshot assert_snapshot name: {name} update: {update}")
    directory = Path(snapshot_dir or DEFAULT_SNAPSHOT_DIR)
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / f"{name}.json"
    sanitized = _strip_keys(payload, ignore_keys or [])
    serialized = json.dumps(sanitized, indent=2, sort_keys=True, ensure_ascii=False)
    if update or not target.exists():
        target.write_text(serialized, encoding="utf-8")
        return
    expected = target.read_text(encoding="utf-8")
    if expected != serialized:
        message = (
            f"snapshot mismatch for {name}. Re-run with update=True to refresh.\n"
            f"--- expected ---\n{expected}\n--- actual ---\n{serialized}"
        )
        apitestka_logger.error(message)
        raise APIAssertException(message)
