from __future__ import annotations

import argparse
import json
import socket
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import icrawler.dashboard as base_dashboard
from icrawler.dashboard import (
    collect_task_overviews,
    create_dashboard_app,
    render_dashboard_html,
)
from searcher.policy_finder import Entry, PolicyFinder, default_state_path

DEFAULT_SEARCH_TOPK = 5
MAX_SEARCH_TOPK = 50

JSONResponse = base_dashboard.JSONResponse
Request = base_dashboard.Request
uvicorn = base_dashboard.uvicorn
_FASTAPI_IMPORT_ERROR = base_dashboard._FASTAPI_IMPORT_ERROR


def _resolve_state_path(task_name: str, override: Optional[str]) -> Path:
    script_dir = Path(__file__).resolve().parent
    if override:
        candidate = Path(override).expanduser()
    else:
        candidate = default_state_path(task_name, script_dir)
    if not candidate.exists():
        alternative = Path("/mnt/data") / candidate.name
        if alternative.exists():
            return alternative
    return candidate


def _prepare_policy_finder(
    *,
    disable_search: bool,
    policy_updates_path: Optional[str],
    regulator_notice_path: Optional[str],
) -> Tuple[Optional[PolicyFinder], Optional[str]]:
    if disable_search:
        return None, "Search disabled by configuration"

    resolved_policy_updates = _resolve_state_path("policy_updates", policy_updates_path)
    resolved_regulator_notice = _resolve_state_path(
        "regulator_notice", regulator_notice_path
    )

    missing: List[str] = []
    for resolved in (resolved_policy_updates, resolved_regulator_notice):
        if not resolved.exists():
            missing.append(str(resolved))
    if missing:
        return None, "Missing search state file(s): " + ", ".join(missing)

    try:
        finder = PolicyFinder(
            str(resolved_policy_updates),
            str(resolved_regulator_notice),
        )
    except Exception as exc:  # pragma: no cover - defensive
        return None, f"Failed to load search index: {exc}"

    return finder, None


def _coerce_search_topk(
    value: Any,
    *,
    default: int = DEFAULT_SEARCH_TOPK,
    limit: int = MAX_SEARCH_TOPK,
) -> int:
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


def _coerce_search_bool(value: Any) -> Optional[bool]:
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


def _search_entry_payload(
    entry: Entry, score: float, include_documents: bool
) -> Dict[str, Any]:
    payload = entry.to_dict(include_documents=include_documents)
    payload["score"] = score
    return payload


def _serve_portal(
    config_path: str,
    host: str,
    port: int,
    *,
    auto_refresh: int,
    task: Optional[str],
    artifact_dir_override: Optional[str],
    policy_finder: Optional[PolicyFinder],
    search_settings: Dict[str, object],
) -> None:
    if JSONResponse is None or Request is None or uvicorn is None:
        raise RuntimeError(
            "FastAPI and uvicorn are required to run the portal. "
            "Install them via `pip install fastapi uvicorn`."
        ) from _FASTAPI_IMPORT_ERROR

    search_default_topk = int(search_settings.get("default_topk", DEFAULT_SEARCH_TOPK))
    search_max_topk = int(search_settings.get("max_topk", MAX_SEARCH_TOPK))
    if search_default_topk <= 0:
        search_default_topk = DEFAULT_SEARCH_TOPK
    if search_max_topk <= 0:
        search_max_topk = MAX_SEARCH_TOPK
    if search_default_topk > search_max_topk:
        search_default_topk = max(1, min(search_default_topk, search_max_topk))

    search_include_documents = bool(search_settings.get("include_documents", True))
    search_reason = search_settings.get("reason")

    search_config_payload: Dict[str, object] = {
        "enabled": policy_finder is not None,
        "endpoint": "/api/search",
        "defaultTopk": search_default_topk,
        "maxTopk": search_max_topk,
        "includeDocuments": search_include_documents,
    }
    if policy_finder is None and isinstance(search_reason, str):
        search_config_payload["reason"] = search_reason

    app = create_dashboard_app(
        config_path,
        auto_refresh=auto_refresh,
        task=task,
        artifact_dir_override=artifact_dir_override,
        search_config=search_config_payload,
    )

    search_finder = policy_finder

    def _search_disabled_response() -> JSONResponse:
        payload: Dict[str, object] = {"error": "search_disabled"}
        if isinstance(search_reason, str):
            payload["reason"] = search_reason
        return JSONResponse(payload, status_code=404)

    def _handle_search(query: str, topk: int, include_documents: bool) -> JSONResponse:
        if search_finder is None:
            return _search_disabled_response()
        results = [
            _search_entry_payload(entry, score, include_documents)
            for entry, score in search_finder.search(query, topk=topk)
        ]
        return JSONResponse(
            {
                "query": query,
                "topk": topk,
                "include_documents": include_documents,
                "result_count": len(results),
                "results": results,
            }
        )

    @app.get("/api/search")
    def search_get(request: Request) -> JSONResponse:
        if search_finder is None:
            return _search_disabled_response()

        params = request.query_params
        query_value = params.get("query") or params.get("q")
        if not query_value or not query_value.strip():
            return JSONResponse({"error": "missing_query"}, status_code=400)
        query = query_value.strip()

        topk_param = params.get("topk")
        try:
            topk = _coerce_search_topk(
                topk_param,
                default=search_default_topk,
                limit=search_max_topk,
            )
        except Exception:
            return JSONResponse({"error": "invalid_topk"}, status_code=400)

        include_documents = search_include_documents
        include_param = params.get("include_documents") or params.get("documents")
        if include_param is not None:
            try:
                parsed_bool = _coerce_search_bool(include_param)
            except Exception:
                return JSONResponse({"error": "invalid_include_documents"}, status_code=400)
            if parsed_bool is not None:
                include_documents = parsed_bool

        return _handle_search(query, topk, include_documents)

    @app.post("/api/search")
    async def search_post(request: Request) -> JSONResponse:
        if search_finder is None:
            return _search_disabled_response()

        content_length = request.headers.get("content-length")
        if content_length:
            try:
                int(content_length)
            except ValueError:
                return JSONResponse({"error": "invalid_content_length"}, status_code=400)

        body = await request.body()
        if not body:
            return JSONResponse({"error": "empty_body"}, status_code=400)

        try:
            payload = json.loads(body.decode("utf-8"))
        except json.JSONDecodeError:
            return JSONResponse({"error": "invalid_json"}, status_code=400)

        if not isinstance(payload, dict):
            return JSONResponse({"error": "invalid_payload"}, status_code=400)

        query_value = payload.get("query") or payload.get("q")
        if not isinstance(query_value, str) or not query_value.strip():
            return JSONResponse({"error": "missing_query"}, status_code=400)
        query = query_value.strip()

        try:
            topk = _coerce_search_topk(
                payload.get("topk"),
                default=search_default_topk,
                limit=search_max_topk,
            )
        except Exception:
            return JSONResponse({"error": "invalid_topk"}, status_code=400)

        include_documents = search_include_documents
        include_value = payload.get("include_documents")
        if include_value is None:
            include_value = payload.get("documents")
        if include_value is not None:
            try:
                parsed_bool = _coerce_search_bool(include_value)
            except Exception:
                return JSONResponse({"error": "invalid_include_documents"}, status_code=400)
            if parsed_bool is not None:
                include_documents = parsed_bool

        return _handle_search(query, topk, include_documents)

    host_display = host
    if host_display == "0.0.0.0":
        try:
            host_display = socket.gethostbyname(socket.gethostname())
        except OSError:  # pragma: no cover - best effort resolution
            host_display = host
    print(
        f"Serving icrawler portal on http://{host_display}:{port} (Ctrl+C to quit)",
        file=sys.stderr,
    )

    uvicorn.run(app, host=host, port=port, log_level="info")


def main(argv: Optional[List[str]] = None) -> None:
    parser = argparse.ArgumentParser(description="Run the icrawler portal")
    parser.add_argument("--config", default="pbc_config.json", help="Path to config file")
    parser.add_argument("--artifact-dir", help="Override artifact directory")
    parser.add_argument("--task", help="Only show a specific task by name")
    parser.add_argument("--host", default="0.0.0.0", help="Portal bind host")
    parser.add_argument("--port", type=int, default=8000, help="Portal port")
    parser.add_argument(
        "--refresh",
        type=int,
        default=30,
        help="Auto-refresh interval in seconds (set 0 to disable)",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Render the dashboard once to stdout and exit",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output the collected overview as JSON and exit",
    )
    parser.add_argument(
        "--disable-search",
        action="store_true",
        help="Disable the policy search interface",
    )
    parser.add_argument(
        "--search-policy-updates",
        help="Path to the policy_updates state JSON for the search interface",
    )
    parser.add_argument(
        "--search-regulator-notice",
        help="Path to the regulator_notice state JSON for the search interface",
    )
    parser.add_argument(
        "--search-default-topk",
        type=int,
        default=DEFAULT_SEARCH_TOPK,
        help="Default top-k value used when searching",
    )
    parser.add_argument(
        "--search-max-topk",
        type=int,
        default=MAX_SEARCH_TOPK,
        help="Maximum allowed top-k when searching",
    )

    args = parser.parse_args(argv)

    config_path = args.config

    overviews = collect_task_overviews(
        config_path,
        task=args.task,
        artifact_dir_override=args.artifact_dir,
    )

    if args.once and args.json:
        print(json.dumps([overview.to_jsonable() for overview in overviews], ensure_ascii=False, indent=2))
        return
    if args.once:
        html = render_dashboard_html(
            overviews,
            generated_at=datetime.now(),
            auto_refresh=args.refresh,
            search_config={
                "enabled": False,
                "reason": "Search is unavailable in static snapshots.",
            },
        )
        print(html)
        return
    if args.json:
        print(json.dumps([overview.to_jsonable() for overview in overviews], ensure_ascii=False, indent=2))
        return

    search_default_topk = (
        args.search_default_topk
        if isinstance(args.search_default_topk, int) and args.search_default_topk > 0
        else DEFAULT_SEARCH_TOPK
    )
    search_max_topk = (
        args.search_max_topk
        if isinstance(args.search_max_topk, int) and args.search_max_topk > 0
        else MAX_SEARCH_TOPK
    )
    if search_default_topk > search_max_topk:
        search_default_topk = min(search_default_topk, search_max_topk)

    policy_finder, search_error = _prepare_policy_finder(
        disable_search=args.disable_search,
        policy_updates_path=args.search_policy_updates,
        regulator_notice_path=args.search_regulator_notice,
    )
    if search_error and not args.disable_search:
        print(f"[portal] Search interface disabled: {search_error}", file=sys.stderr)

    _serve_portal(
        config_path,
        args.host,
        args.port,
        auto_refresh=args.refresh,
        task=args.task,
        artifact_dir_override=args.artifact_dir,
        policy_finder=policy_finder,
        search_settings={
            "default_topk": search_default_topk,
            "max_topk": search_max_topk,
            "include_documents": True,
            "reason": search_error,
        },
    )


if __name__ == "__main__":
    main()
