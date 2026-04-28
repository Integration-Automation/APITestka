"""
Record-replay proxy for the mock server.

When live, every request hits the upstream URL and the round trip is recorded
into a Cassette. When replaying, the cassette serves the response without ever
touching the network.
"""
from __future__ import annotations

import json
from typing import Optional

from flask import Flask, Response, request

import httpx

from je_api_testka.connection.cassette import Cassette, CassetteRecord


def attach_proxy(
    app: Flask,
    upstream_base: str,
    cassette_path: str,
    route: str = "/proxy/<path:upstream_path>",
    timeout: float = 30.0,
    replay_only: bool = False,
) -> None:
    """Mount a proxy endpoint on ``app`` that records or replays through ``cassette_path``."""
    cassette = Cassette(cassette_path)

    def _view(upstream_path: str):
        method = request.method
        url = f"{upstream_base.rstrip('/')}/{upstream_path}"
        body = request.get_data(as_text=True)
        cached: Optional[CassetteRecord] = cassette.get(method, url, body)
        if cached is not None:
            return Response(
                cached.response_body,
                status=cached.response_status,
                headers=cached.response_headers,
            )
        if replay_only:
            return Response(
                json.dumps({"error": "no cassette entry"}),
                status=404,
                mimetype="application/json",
            )
        live = httpx.request(
            method,
            url,
            content=body or None,
            headers={k: v for k, v in request.headers.items() if k.lower() != "host"},
            timeout=timeout,
        )
        record = CassetteRecord(
            method=method,
            url=url,
            request_body=body,
            response_status=live.status_code,
            response_body=live.text,
            response_headers=dict(live.headers.items()),
        )
        cassette.put(record)
        return Response(record.response_body, status=record.response_status,
                        headers=record.response_headers)

    _view.__name__ = "proxy_recorder_view"
    app.route(route, methods=["GET", "POST", "PUT", "PATCH", "DELETE"])(_view)
