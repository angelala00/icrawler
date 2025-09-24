#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FastAPI server exposing :mod:`searcher.policy_finder`.

The API mirrors the previous simple HTTP server but is now powered by
`FastAPI <https://fastapi.tiangolo.com/>`_.  Example usage from the command
line::

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
from pathlib import Path
from typing import Any, Dict, Mapping, Optional, Tuple

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response

from .policy_finder import (
    Entry,
    PolicyFinder,
    default_state_path,
    parse_clause_reference,
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


def _search_payload(
    finder: PolicyFinder,
    query: str,
    topk: int,
    include_documents: bool,
) -> Dict[str, Any]:
    clause_ref = parse_clause_reference(query)
    results_payload = []
    for entry, score in finder.search(query, topk=topk):
        payload = _entry_payload(entry, score, include_documents)
        if clause_ref is not None:
            clause_result = finder.extract_clause(entry, clause_ref)
            payload["clause"] = clause_result.to_dict()
        results_payload.append(payload)

    response: Dict[str, Any] = {
        "query": query,
        "topk": topk,
        "result_count": len(results_payload),
        "results": results_payload,
    }
    if clause_ref is not None:
        response["clause_reference"] = clause_ref.to_dict()
    return response


def _parse_search_params(
    params: Mapping[str, Any],
    *,
    query_error: str,
    topk_error: str,
    include_error: str,
) -> Tuple[str, int, bool]:
    query_text = ""
    for key in ("query", "q"):
        value = params.get(key)
        if isinstance(value, str):
            stripped = value.strip()
            if stripped:
                query_text = stripped
                break
    if not query_text:
        raise ValueError(query_error)

    try:
        topk_value = _coerce_topk(params.get("topk"))
    except Exception as exc:  # pragma: no cover - defensive branch
        raise ValueError(topk_error) from exc

    include_flag = True
    include_value = params.get("include_documents")
    if include_value is None:
        include_value = params.get("documents")
    if include_value is not None:
        try:
            parsed_bool = _coerce_bool(include_value)
        except Exception as exc:  # pragma: no cover - defensive branch
            raise ValueError(include_error) from exc
        if parsed_bool is not None:
            include_flag = parsed_bool

    return query_text, topk_value, include_flag


def create_app(finder: PolicyFinder) -> FastAPI:
    """Create and configure a FastAPI application for the policy finder."""

    app = FastAPI(title="Policy Finder API", version="1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.state.finder = finder

    def get_finder(request: Request) -> PolicyFinder:
        finder_instance = getattr(request.app.state, "finder", None)
        if finder_instance is None:
            raise HTTPException(status_code=503, detail="Policy finder not configured")
        return finder_instance

    def bad_request(message: str) -> JSONResponse:
        LOGGER.debug("Bad request: %s", message)
        return JSONResponse(status_code=400, content={"error": message})

    @app.get("/")
    def root() -> Dict[str, Any]:
        return {"service": "policy_finder", "endpoints": ["/search"]}

    @app.get("/health")
    @app.get("/healthz")
    @app.get("/ping")
    def health() -> Dict[str, str]:
        return {"status": "ok"}

    @app.options("/search")
    def options_search() -> Response:
        return Response(status_code=204)

    @app.get("/search")
    def search_get(
        query: Optional[str] = Query(None),
        q: Optional[str] = Query(None),
        topk: Optional[str] = Query(None),
        include_documents: Optional[str] = Query(None),
        documents: Optional[str] = Query(None),
        finder_instance: PolicyFinder = Depends(get_finder),
    ) -> JSONResponse:
        params = {
            "query": query,
            "q": q,
            "topk": topk,
            "include_documents": include_documents,
            "documents": documents,
        }
        try:
            query_text, topk_value, include_flag = _parse_search_params(
                params,
                query_error="Missing 'query' parameter",
                topk_error="Invalid 'topk' parameter",
                include_error="Invalid 'include_documents' parameter",
            )
        except ValueError as exc:
            return bad_request(str(exc))

        payload = _search_payload(finder_instance, query_text, topk_value, include_flag)
        return JSONResponse(status_code=200, content=payload)

    @app.post("/search")
    async def search_post(
        request: Request,
        finder_instance: PolicyFinder = Depends(get_finder),
    ) -> JSONResponse:
        body = await request.body()
        if not body:
            return bad_request("Empty request body")

        try:
            payload = json.loads(body.decode("utf-8"))
        except json.JSONDecodeError:
            return bad_request("Request body must be valid JSON")

        if not isinstance(payload, dict):
            return bad_request("Request body must be a JSON object")

        try:
            query_text, topk_value, include_flag = _parse_search_params(
                payload,
                query_error="Field 'query' is required",
                topk_error="Field 'topk' must be a positive integer",
                include_error="Field 'include_documents' must be boolean",
            )
        except ValueError as exc:
            return bad_request(str(exc))

        payload_data = _search_payload(finder_instance, query_text, topk_value, include_flag)
        return JSONResponse(status_code=200, content=payload_data)

    return app


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

    app = create_app(finder)
    host = args.host
    port = args.port
    LOGGER.info("Serving policy finder API on %s:%s", host, port)

    try:
        uvicorn.run(app, host=host, port=port, log_level="info")
    except KeyboardInterrupt:
        LOGGER.info("Stopping policy finder API")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
