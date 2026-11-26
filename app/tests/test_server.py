"""Unit and HTTP contract tests for demo-service."""

from __future__ import annotations

import json
import threading
import urllib.error
import urllib.request
from typing import Iterator

import pytest

from src.server import create_server


@pytest.fixture()
def live_server() -> Iterator[str]:
    server = create_server("127.0.0.1", 0)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_healthz_and_security_headers(live_server: str) -> None:
    with urllib.request.urlopen(f"{live_server}/healthz", timeout=3) as resp:
        assert resp.status == 200
        assert resp.headers["X-Content-Type-Options"] == "nosniff"
        assert resp.headers["X-Frame-Options"] == "DENY"
        assert "default-src 'none'" in resp.headers["Content-Security-Policy"]
        payload = json.loads(resp.read().decode("utf-8"))
        assert payload == {"status": "alive"}


def test_readyz(live_server: str) -> None:
    with urllib.request.urlopen(f"{live_server}/readyz", timeout=3) as resp:
        assert resp.status == 200
        assert json.loads(resp.read().decode("utf-8")) == {"status": "ready"}


def test_info_endpoint(live_server: str) -> None:
    with urllib.request.urlopen(f"{live_server}/api/v1/info", timeout=3) as resp:
        assert resp.status == 200
        payload = json.loads(resp.read().decode("utf-8"))
        assert payload["service"] == "demo-service"
        assert "version" in payload
        assert "environment" in payload


def test_metrics_endpoint(live_server: str) -> None:
    urllib.request.urlopen(f"{live_server}/healthz", timeout=3).read()
    with urllib.request.urlopen(f"{live_server}/metrics", timeout=3) as resp:
        assert resp.status == 200
        body = resp.read().decode("utf-8")
        assert "demo_service_uptime_seconds" in body
        assert 'demo_service_http_requests_total{path="/healthz",status="200"}' in body


def test_not_found(live_server: str) -> None:
    with pytest.raises(urllib.error.HTTPError) as exc_info:
        urllib.request.urlopen(f"{live_server}/does-not-exist", timeout=3)
    assert exc_info.value.code == 404
