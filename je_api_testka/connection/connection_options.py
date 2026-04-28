"""
Unified connection options applied across the requests / httpx wrappers.

* mTLS via ``cert``
* Proxy via ``proxies`` (HTTP / HTTPS / SOCKS string formats accepted)
* SSL ``verify`` flag (CA bundle path or bool)
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple, Union


@dataclass
class ConnectionOptions:
    """Shared knobs that apply to both backends."""

    cert: Optional[Union[str, Tuple[str, str]]] = None
    proxies: Optional[dict] = None
    verify: Union[bool, str] = True


def apply_to_requests_kwargs(options: ConnectionOptions, kwargs: dict) -> dict:
    """Merge :class:`ConnectionOptions` into a ``requests`` kwargs dict."""
    merged = dict(kwargs)
    if options.cert is not None:
        merged["cert"] = options.cert
    if options.proxies is not None:
        merged["proxies"] = options.proxies
    merged.setdefault("verify", options.verify)
    return merged


def apply_to_httpx_kwargs(options: ConnectionOptions, kwargs: dict) -> dict:
    """Merge into an ``httpx`` kwargs dict (proxy key is ``proxies``)."""
    merged = dict(kwargs)
    if options.cert is not None:
        merged["cert"] = options.cert
    if options.proxies is not None:
        merged["proxies"] = options.proxies
    merged.setdefault("verify", options.verify)
    return merged
