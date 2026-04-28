"""Tests for shared connection options."""
from __future__ import annotations

from je_api_testka.connection.connection_options import (
    ConnectionOptions,
    apply_to_httpx_kwargs,
    apply_to_requests_kwargs,
)


def test_apply_to_requests_merges_cert_and_proxy():
    options = ConnectionOptions(cert=("c.crt", "c.key"), proxies={"http": "http://p.invalid"})
    merged = apply_to_requests_kwargs(options, {"timeout": 5})
    assert merged["cert"] == ("c.crt", "c.key")
    assert merged["proxies"] == {"http": "http://p.invalid"}
    assert merged["timeout"] == 5


def test_apply_to_httpx_uses_verify_from_options():
    options = ConnectionOptions(verify="/etc/ssl/ca.pem")
    merged = apply_to_httpx_kwargs(options, {})
    assert merged["verify"] == "/etc/ssl/ca.pem"


def test_existing_verify_kwarg_wins():
    options = ConnectionOptions(verify=False)
    merged = apply_to_requests_kwargs(options, {"verify": True})
    assert merged["verify"] is True
