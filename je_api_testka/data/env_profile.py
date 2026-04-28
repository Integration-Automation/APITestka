"""
Environment profile loader.

A profile is a JSON file mapping variable names to values. ``load_env_profile``
reads the file, sets each entry into the global :data:`variable_store`, and
returns an :class:`EnvProfile` describing what was loaded.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

from je_api_testka.data.variable_store import VariableStore, variable_store


@dataclass
class EnvProfile:
    """Loaded environment data plus the file it came from."""

    name: str
    values: Dict[str, str]
    source: Path


def load_env_profile(file_path: str, store: Optional[VariableStore] = None) -> EnvProfile:
    """Read ``file_path`` and apply each key/value into ``store``."""
    active_store = store or variable_store
    target = Path(file_path)
    raw = json.loads(target.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise TypeError(f"env profile must be a JSON object, got {type(raw).__name__}")
    for key, value in raw.items():
        active_store.set(key, value)
    return EnvProfile(name=target.stem, values={k: str(v) for k, v in raw.items()}, source=target)
