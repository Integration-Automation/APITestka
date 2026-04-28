"""
Headless model for the GUI environment-manager panel.

Stores environment definitions (a name plus a key/value mapping) and emits
them as :class:`EnvProfile`-compatible dicts for the variable store.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

from je_api_testka.data.variable_store import variable_store


@dataclass
class EnvironmentDefinition:
    """One named environment as managed by the GUI."""

    name: str
    values: Dict[str, str] = field(default_factory=dict)


class EnvManagerModel:
    """Mutable list of :class:`EnvironmentDefinition` with serialise/load helpers."""

    def __init__(self) -> None:
        self._envs: Dict[str, EnvironmentDefinition] = {}
        self._active: str = ""

    @property
    def active(self) -> str:
        return self._active

    def upsert(self, name: str, values: Dict[str, str]) -> None:
        self._envs[name] = EnvironmentDefinition(name=name, values=dict(values))

    def remove(self, name: str) -> None:
        self._envs.pop(name, None)
        if self._active == name:
            self._active = ""

    def list_envs(self) -> List[EnvironmentDefinition]:
        return list(self._envs.values())

    def activate(self, name: str) -> None:
        if name not in self._envs:
            raise KeyError(name)
        self._active = name
        for key, value in self._envs[name].values.items():
            variable_store.set(key, value)

    def export_to_file(self, file_path: str) -> Path:
        target = Path(file_path)
        payload = {env.name: env.values for env in self._envs.values()}
        target.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        return target

    def import_from_file(self, file_path: str) -> None:
        raw = json.loads(Path(file_path).read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            raise TypeError("environment file must be a JSON object")
        for name, values in raw.items():
            if not isinstance(values, dict):
                continue
            self.upsert(name, {str(k): str(v) for k, v in values.items()})
