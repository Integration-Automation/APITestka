"""Tests for socket.getaddrinfo override."""
from __future__ import annotations

import socket

from je_api_testka.connection.dns_override import dns_override


def test_dns_override_remaps_known_host():
    captured = {}
    real = socket.getaddrinfo

    def _spy(host, port, *args, **kwargs):
        captured["host"] = host
        return [(socket.AF_INET, socket.SOCK_STREAM, 0, "", (host, port))]

    socket.getaddrinfo = _spy
    try:
        with dns_override({"example.invalid": "127.0.0.1"}):
            socket.getaddrinfo("example.invalid", 80)
        assert captured["host"] == "127.0.0.1"
    finally:
        socket.getaddrinfo = real


def test_dns_override_passes_through_unknown_host():
    captured = {}
    real = socket.getaddrinfo

    def _spy(host, port, *args, **kwargs):
        captured["host"] = host
        return []

    socket.getaddrinfo = _spy
    try:
        with dns_override({"example.invalid": "127.0.0.1"}):
            socket.getaddrinfo("other.invalid", 80)
        assert captured["host"] == "other.invalid"
    finally:
        socket.getaddrinfo = real


def test_dns_override_restores_after_block():
    real = socket.getaddrinfo
    with dns_override({"example.invalid": "127.0.0.1"}):
        # entering and immediately exiting is what we want to verify;
        # the assertion below proves the patch is reverted on __exit__.
        assert socket.getaddrinfo is not real
    assert socket.getaddrinfo is real
