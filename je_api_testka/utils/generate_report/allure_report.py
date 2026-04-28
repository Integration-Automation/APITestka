"""
Generate Allure-compatible JSON result files.

Each test record becomes one ``*-result.json`` file in the target directory,
which Allure picks up via ``allure generate``.
"""
from __future__ import annotations

import json
import time
import uuid
from pathlib import Path
from typing import List

from je_api_testka.utils.logging.loggin_instance import apitestka_logger
from je_api_testka.utils.test_record.test_record_class import test_record_instance

DEFAULT_ALLURE_DIR: str = "allure-results"
ALLURE_PASSED: str = "passed"
ALLURE_FAILED: str = "failed"


def _now_ms() -> int:
    return int(time.time() * 1000)


def _write_result(directory: Path, payload: dict) -> Path:
    target = directory / f"{uuid.uuid4().hex}-result.json"
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return target


def generate_allure_report(directory: str = DEFAULT_ALLURE_DIR) -> List[Path]:
    """Materialise the global test record as Allure result files."""
    apitestka_logger.info(f"allure_report generate_allure_report directory: {directory}")
    output_dir = Path(directory)
    output_dir.mkdir(parents=True, exist_ok=True)
    written: List[Path] = []

    base_time = _now_ms()
    for index, record in enumerate(test_record_instance.test_record_list, start=1):
        payload = {
            "uuid": uuid.uuid4().hex,
            "name": str(record.get("request_url") or f"success_{index}"),
            "status": ALLURE_PASSED,
            "stage": "finished",
            "start": base_time,
            "stop": base_time,
            "labels": [{"name": "framework", "value": "APITestka"}],
            "parameters": [
                {"name": "method", "value": str(record.get("request_method"))},
                {"name": "status_code", "value": str(record.get("status_code"))},
            ],
        }
        written.append(_write_result(output_dir, payload))

    for index, record in enumerate(test_record_instance.error_record_list, start=1):
        meta = record[0] if record and isinstance(record[0], dict) else {}
        message = record[1] if len(record) > 1 else ""
        payload = {
            "uuid": uuid.uuid4().hex,
            "name": str(meta.get("test_url") or f"failure_{index}"),
            "status": ALLURE_FAILED,
            "stage": "finished",
            "start": base_time,
            "stop": base_time,
            "statusDetails": {"message": str(message), "trace": ""},
            "labels": [{"name": "framework", "value": "APITestka"}],
        }
        written.append(_write_result(output_dir, payload))
    return written
