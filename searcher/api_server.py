#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Simple HTTP API for :mod:`searcher.policy_finder`.

The server exposes a ``/search`` endpoint that mirrors the command line tool
but returns JSON responses suitable for automation. Example usage::

    python -m searcher.api_server --host 0.0.0.0 --port 8080

Once running, issue requests such as::

    curl "http://localhost:8080/search?query=金融监管"  # GET request

or::

    curl -X POST -H "Content-Type: application/json" \
         -d '{"query": "监管文件", "topk": 3}' \
         http://localhost:8080/search
"""

from __future__ import annotations

import argparse
import json
import logging
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
from urllib.parse import parse_qs, urlparse

from .policy_finder import (
    Entry,
    PolicyFinder,
    default_state_path,
)

LOGGER = logging.getLogger("searcher.api")


def _coerce_topk(value: Any, default: int = 5, limit: int = 50) -> int:
    if value is None:
        return default
    if isinstance(value, bool):
        raise ValueError("Boolean is not valid for topk")
    if isinstance(value, (int, float)):
        candidate = int(value)
    elif isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return default
        candidate = int(stripped)
    else:
        raise ValueError("Unsupported type for topk")
    if candidate <= 0:
        raise ValueError("topk must be positive")
    return max(1, min(limit, candidate))


def _coerce_bool(value: Any) -> Optional[bool]:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(int(value))
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"1", "true", "yes", "on"}:
            return True
        if lowered in {"0", "false", "no", "off"}:
            return False
    raise ValueError("Invalid boolean value")


def _entry_payload(entry: Entry, score: float, include_documents: bool) -> Dict[str, Any]:
    payload = entry.to_dict(include_documents=include_documents)
    payload["score"] = score
    return payload


def _resolve_json_path(value: Optional[str], fallback: Path) -> Path:
    if value:
        candidate = Path(value).expanduser()
    else:
        candidate = fallback
    if not candidate.exists():
        alt = Path("/mnt/data") / candidate.name
        if alt.exists():
            return alt
    return candidate


def _make_handler(finder: PolicyFinder):
    class PolicyFinderHandler(BaseHTTPRequestHandler):
        server_version = "PolicyFinderAPI/1.0"
        finder_instance = finder

        def _send_json(self, status: int, payload: Dict[str, Any]) -> None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(body)

        def _handle_search(self, query: str, topk: int, include_documents: bool) -> None:
            results = [
                _entry_payload(entry, score, include_documents)
                for entry, score in self.finder_instance.search(query, topk=topk)
            ]
            self._send_json(
                200,
                {
                    "query": query,
                    "topk": topk,
                    "result_count": len(results),
                    "results": results,
                },
            )

        def _bad_request(self, message: str) -> None:
            LOGGER.debug("Bad request: %s", message)
            self._send_json(400, {"error": message})

        def do_OPTIONS(self) -> None:  # noqa: N802 (HTTP verb method name)
            parsed = urlparse(self.path)
            if parsed.path == "/search":
                self.send_response(204)
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
                self.send_header("Access-Control-Allow-Headers", "Content-Type")
                self.end_headers()
                return
            self.send_response(404)
            self.end_headers()

        def do_GET(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            if parsed.path in {"/health", "/healthz", "/ping"}:
                self._send_json(200, {"status": "ok"})
                return
            if parsed.path in {"", "/"}:
                self._send_json(200, {"service": "policy_finder", "endpoints": ["/search"]})
                return
            if parsed.path != "/search":
                self._send_json(404, {"error": "not_found"})
                return

            params = parse_qs(parsed.query)
            query_values = params.get("query") or params.get("q")
            if not query_values or not query_values[0].strip():
                self._bad_request("Missing 'query' parameter")
                return
            query = query_values[0].strip()

            topk_param = params.get("topk", [None])[0]
            try:
                topk = _coerce_topk(topk_param)
            except Exception:
                self._bad_request("Invalid 'topk' parameter")
                return

            include_documents = True
            include_param = params.get("include_documents") or params.get("documents")
            if include_param and include_param[0] is not None:
                try:
                    parsed_bool = _coerce_bool(include_param[0])
                except Exception:
                    self._bad_request("Invalid 'include_documents' parameter")
                    return
                if parsed_bool is not None:
                    include_documents = parsed_bool

            self._handle_search(query, topk, include_documents)

        def do_POST(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            if parsed.path != "/search":
                self._send_json(404, {"error": "not_found"})
                return

            content_length = self.headers.get("Content-Length")
            try:
                length = int(content_length) if content_length else 0
            except ValueError:
                self._bad_request("Invalid Content-Length header")
                return

            data = self.rfile.read(length) if length > 0 else b""
            if not data:
                self._bad_request("Empty request body")
                return

            try:
                payload = json.loads(data.decode("utf-8"))
            except json.JSONDecodeError:
                self._bad_request("Request body must be valid JSON")
                return

            query = payload.get("query") or payload.get("q")
            if not isinstance(query, str) or not query.strip():
                self._bad_request("Field 'query' is required")
                return
            query = query.strip()

            try:
                topk = _coerce_topk(payload.get("topk"))
            except Exception:
                self._bad_request("Field 'topk' must be a positive integer")
                return

            include_documents = True
            if "include_documents" in payload:
                try:
                    parsed_bool = _coerce_bool(payload.get("include_documents"))
                except Exception:
                    self._bad_request("Field 'include_documents' must be boolean")
                    return
                if parsed_bool is not None:
                    include_documents = parsed_bool

            self._handle_search(query, topk, include_documents)

        def log_message(self, fmt: str, *args: Any) -> None:
            LOGGER.info("%s - %s", self.address_string(), fmt % args)

    return PolicyFinderHandler


def build_server(finder: PolicyFinder, host: str, port: int) -> ThreadingHTTPServer:
    handler = _make_handler(finder)
    return ThreadingHTTPServer((host, port), handler)


def parse_args(argv: Optional[Tuple[str, ...]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Policy finder HTTP API")
    parser.add_argument("--host", default="0.0.0.0", help="Bind address (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8001, help="Port to bind (default: 8001)")
    parser.add_argument(
        "--policy-updates",
        help="Path to policy_updates state JSON (defaults to autodiscovery)",
    )
    parser.add_argument(
        "--regulator-notice",
        help="Path to regulator_notice state JSON (defaults to autodiscovery)",
    )
    return parser.parse_args(argv)


def main(argv: Optional[Tuple[str, ...]] = None) -> int:
    args = parse_args(argv)

    if not logging.getLogger().handlers:
        logging.basicConfig(level=logging.INFO)

    script_dir = Path(__file__).resolve().parent
    default_policy_updates = default_state_path("policy_updates", script_dir)
    default_regulator_notice = default_state_path("regulator_notice", script_dir)

    policy_updates_path = _resolve_json_path(args.policy_updates, default_policy_updates)
    regulator_notice_path = _resolve_json_path(args.regulator_notice, default_regulator_notice)

    finder = PolicyFinder(str(policy_updates_path), str(regulator_notice_path))

    server = build_server(finder, args.host, args.port)
    host, port = server.server_address[:2]
    LOGGER.info("Serving policy finder API on %s:%s", host, port)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        LOGGER.info("Stopping policy finder API")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
