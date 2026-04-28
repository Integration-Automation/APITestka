"""
Context manager that overrides ``socket.getaddrinfo`` to map specific hostnames
to specific IPs. Useful for testing staging endpoints against prod IPs without
editing /etc/hosts.
"""
from __future__ import annotations

import socket
from contextlib import contextmanager
from typing import Iterator, Mapping


@contextmanager
def dns_override(mapping: Mapping[str, str]) -> Iterator[None]:
    """Within the ``with`` block, hosts in ``mapping`` resolve to the given IP strings."""
    original = socket.getaddrinfo

    def _patched(host, port, *args, **kwargs):
        target = mapping.get(host, host)
        return original(target, port, *args, **kwargs)

    socket.getaddrinfo = _patched
    try:
        yield
    finally:
        socket.getaddrinfo = original
