"""
Match concrete request paths against OpenAPI path templates.

``/items/{id}`` matches ``/items/42``: each ``{name}`` segment matches one
non-empty path segment. When several templates match, the one with the most
literal segments wins, so ``/items/latest`` beats ``/items/{id}`` for
``/items/latest``, as OpenAPI requires.
"""
from __future__ import annotations

import re
from typing import Iterable, Optional, Pattern
from urllib.parse import urlparse

_PARAMETER = re.compile(r"\{[^/{}]+\}")


def template_regex(template: str) -> Pattern[str]:
    """Return a regex that matches the concrete paths of ``template``."""
    parts = _PARAMETER.split(template)
    return re.compile("^" + "[^/]+".join(re.escape(part) for part in parts) + "$")


def _literal_segments(template: str) -> int:
    return sum(1 for segment in template.split("/") if segment and not _PARAMETER.fullmatch(segment))


def match_path_template(path: str, templates: Iterable[str]) -> Optional[str]:
    """Return the template in ``templates`` that best matches ``path``, or ``None``."""
    matches = [template for template in templates if template_regex(template).match(path)]
    if not matches:
        return None
    return max(matches, key=_literal_segments)


_ID_SEGMENT = re.compile(
    r"^(?:\d+|[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}|[0-9a-fA-F]{16,})$"
)


def generalize_path(path: str) -> str:
    """
    Replace identifier-like segments with parameters: ``/users/42/orders/7`` → ``/users/{id}/orders/{id2}``.

    Numbers, UUIDs and hexadecimal runs of 16 or more characters count as identifiers.
    """
    count = 0
    segments = []
    for segment in path.split("/"):
        if _ID_SEGMENT.match(segment):
            count += 1
            segments.append("{id}" if count == 1 else f"{{id{count}}}")
        else:
            segments.append(segment)
    return "/".join(segments)


def server_base_path(spec: dict) -> str:
    """Return the path part of the spec's first server URL without a trailing slash (``""`` if none)."""
    servers = spec.get("servers") or []
    url = servers[0].get("url", "") if servers and isinstance(servers[0], dict) else ""
    return urlparse(url).path.rstrip("/")


def strip_base_path(path: str, base_path: str) -> str:
    """Remove ``base_path`` from the front of ``path`` when present (``/api/v1/items`` → ``/items``)."""
    if base_path and (path == base_path or path.startswith(base_path + "/")):
        return path[len(base_path):] or "/"
    return path
