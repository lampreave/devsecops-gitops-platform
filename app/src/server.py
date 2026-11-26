"""Minimal, zero-external-dependency HTTP service for DevSecOps & GitOps demos.

Exposes:
  - GET /healthz      Liveness probe
  - GET /readyz       Readiness probe
  - GET /api/v1/info  Service metadata (version, environment)
  - GET /metrics      Prometheus text exposition metrics
"""

from __future__ import annotations

import json
import logging
import os
import signal
import sys
import threading
import time
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format='{"timestamp":"%(asctime)s","level":"%(levelname)s","message":"%(message)s"}',
    stream=sys.stdout,
)
LOGGER = logging.getLogger("demo-service")

APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
APP_ENV = os.getenv("APP_ENV", "dev")
START_TIME = time.monotonic()

_METRICS_LOCK = threading.Lock()
_REQUEST_COUNTS: dict[tuple[str, int], int] = {}
_READY = True


def _record_metric(path: str, status: int) -> None:
    with _METRICS_LOCK:
        key = (path, status)
        _REQUEST_COUNTS[key] = _REQUEST_COUNTS.get(key, 0) + 1


def render_prometheus_metrics() -> str:
    uptime = max(0.0, time.monotonic() - START_TIME)
    lines = [
        "# HELP demo_service_uptime_seconds Process uptime in seconds.",
        "# TYPE demo_service_uptime_seconds gauge",
        f"demo_service_uptime_seconds {uptime:.2f}",
        "# HELP demo_service_http_requests_total Total HTTP requests processed.",
        "# TYPE demo_service_http_requests_total counter",
    ]
    with _METRICS_LOCK:
        for (path, status), count in sorted(_REQUEST_COUNTS.items()):
            safe_path = path.replace('"', "")
            lines.append(
                f'demo_service_http_requests_total{{path="{safe_path}",status="{status}"}} {count}'
            )
    return "\n".join(lines) + "\n"


class DemoHandler(BaseHTTPRequestHandler):
    """Hardened HTTP request handler with security response headers."""

    server_version = "demo-service"
    sys_version = ""

    def _send_security_headers(self) -> None:
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Content-Security-Policy", "default-src 'none'; frame-ancestors 'none'")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Cache-Control", "no-store")

    def _send_json(self, status: HTTPStatus, payload: dict[str, Any]) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self._send_security_headers()
        self.end_headers()
        self.wfile.write(body)
        _record_metric(self.path, int(status))

    def _send_text(self, status: HTTPStatus, body_text: str, content_type: str) -> None:
        body = body_text.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self._send_security_headers()
        self.end_headers()
        self.wfile.write(body)
        _record_metric(self.path, int(status))

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/healthz":
            self._send_json(HTTPStatus.OK, {"status": "alive"})
        elif self.path == "/readyz":
            if _READY:
                self._send_json(HTTPStatus.OK, {"status": "ready"})
            else:
                self._send_json(HTTPStatus.SERVICE_UNAVAILABLE, {"status": "draining"})
        elif self.path in ("/", "/api/v1/info"):
            self._send_json(
                HTTPStatus.OK,
                {
                    "service": "demo-service",
                    "version": APP_VERSION,
                    "environment": APP_ENV,
                },
            )
        elif self.path == "/metrics":
            self._send_text(
                HTTPStatus.OK,
                render_prometheus_metrics(),
                "text/plain; version=0.0.4; charset=utf-8",
            )
        else:
            self._send_json(HTTPStatus.NOT_FOUND, {"error": "not_found"})

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
        LOGGER.info("request client=%s msg=%s", self.client_address[0], format % args)


def create_server(host: str = "0.0.0.0", port: int = 8080) -> ThreadingHTTPServer:
    return ThreadingHTTPServer((host, port), DemoHandler)


def main() -> None:
    global _READY
    host = os.getenv("APP_HOST", "0.0.0.0")
    port = int(os.getenv("APP_PORT", "8080"))
    server = create_server(host, port)

    def _handle_shutdown(signum: int, _frame: Any) -> None:
        global _READY
        LOGGER.info("shutdown signal=%s draining=true", signum)
        _READY = False
        threading.Thread(target=server.shutdown, daemon=True).start()

    signal.signal(signal.SIGTERM, _handle_shutdown)
    signal.signal(signal.SIGINT, _handle_shutdown)

    LOGGER.info("listening host=%s port=%s env=%s version=%s", host, port, APP_ENV, APP_VERSION)
    try:
        server.serve_forever()
    finally:
        server.server_close()
        LOGGER.info("server stopped cleanly")


if __name__ == "__main__":
    main()
