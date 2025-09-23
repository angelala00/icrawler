from __future__ import annotations

import argparse
import functools
import json
import mimetypes
import os
import socket
import sys
import threading
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple
from urllib.parse import parse_qs, urlsplit

from . import pbc_monitor as core
from .fetching import build_cache_path_for_url
from .runner import (
    _build_tasks,
    _prepare_cache_behavior,
    _prepare_http_options,
    _prepare_task_layout,
)
from .state import PBCState
from searcher.policy_finder import Entry, PolicyFinder, default_state_path


WEB_DIR = Path(__file__).resolve().parent.parent / "web"

DEFAULT_SEARCH_TOPK = 5
MAX_SEARCH_TOPK = 50


@dataclass
class TaskOverview:
    name: str
    start_url: str
    entries_total: int
    documents_total: int
    downloaded_total: int
    pending_total: int
    entries_without_documents: int
    tracked_files: int
    tracked_downloaded: int
    document_type_counts: Dict[str, int]
    state_file: Optional[str]
    state_last_updated: Optional[datetime]
    output_dir: Optional[str]
    output_files: int
    output_size_bytes: int
    page_cache_dir: Optional[str]
    pages_cached: int
    page_cache_fresh: bool
    page_cache_last_fetch: Optional[datetime]
    delay: float
    jitter: float
    timeout: float
    min_hours: float
    max_hours: float
    next_run_earliest: Optional[datetime]
    next_run_latest: Optional[datetime]
    status: str
    status_reason: str
    parser_spec: Optional[str]

    def to_jsonable(self) -> Dict[str, object]:
        def _dt(value: Optional[datetime]) -> Optional[str]:
            if value is None:
                return None
            return value.isoformat(timespec="seconds")

        data = asdict(self)
        data["state_last_updated"] = _dt(self.state_last_updated)
        data["page_cache_last_fetch"] = _dt(self.page_cache_last_fetch)
        data["next_run_earliest"] = _dt(self.next_run_earliest)
        data["next_run_latest"] = _dt(self.next_run_latest)
        return data


def _default_runner_args(task: Optional[str] = None) -> argparse.Namespace:
    return argparse.Namespace(
        start_url=None,
        output_dir=None,
        verify_local=False,
        state_file=None,
        task=task,
        delay=None,
        jitter=None,
        timeout=None,
        min_hours=None,
        max_hours=None,
        refresh_pages=False,
        use_cached_pages=False,
        no_use_cached_pages=False,
        cache_listing=False,
        build_structure=None,
        download_from_structure=None,
        cache_start_page=None,
        preview_page=None,
    )


def _load_config(path: str) -> Dict[str, object]:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _count_files(directory: Optional[str]) -> int:
    if not directory or not os.path.isdir(directory):
        return 0
    total = 0
    for _, _, files in os.walk(directory):
        total += len(files)
    return total


def _sum_file_sizes(directory: Optional[str]) -> int:
    if not directory or not os.path.isdir(directory):
        return 0
    total = 0
    for root, _, files in os.walk(directory):
        for filename in files:
            try:
                total += os.path.getsize(os.path.join(root, filename))
            except OSError:
                continue
    return total


def _count_pages(directory: Optional[str]) -> int:
    if not directory or not os.path.isdir(directory):
        return 0
    total = 0
    for root, _, files in os.walk(directory):
        for filename in files:
            if filename.lower().endswith(".html") or filename.lower().endswith(".htm"):
                total += 1
    return total


def _safe_mtime(path: Optional[str]) -> Optional[datetime]:
    if not path or not os.path.exists(path):
        return None
    try:
        mtime = os.path.getmtime(path)
    except OSError:
        return None
    return datetime.fromtimestamp(mtime)


def _document_type_counts(state: PBCState) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for record in state.files.values():
        if not isinstance(record, dict):
            continue
        key = str(record.get("type") or "unknown")
        counts[key] = counts.get(key, 0) + 1
    return counts


def _compute_status(
    entries_total: int,
    pending_total: int,
    page_cache_fresh: bool,
    pages_cached: int,
) -> (str, str):
    if entries_total == 0:
        return "waiting", "No entries recorded yet"
    if pending_total > 0:
        return "attention", f"{pending_total} document(s) pending download"
    if not page_cache_fresh and pages_cached:
        return "stale", "Listing cache is older than today"
    return "ok", "Up to date"


def collect_task_overviews(
    config_path: str,
    *,
    task: Optional[str] = None,
    artifact_dir_override: Optional[str] = None,
) -> List[TaskOverview]:
    config = _load_config(config_path)
    if artifact_dir_override:
        config["artifact_dir"] = artifact_dir_override
    artifact_dir = str(config.get("artifact_dir") or ".")
    runner_args = _default_runner_args(task)
    tasks = _build_tasks(runner_args, config, artifact_dir)
    overviews: List[TaskOverview] = []

    for spec in tasks:
        layout = _prepare_task_layout(spec, runner_args, config, artifact_dir)
        http_options = _prepare_http_options(spec, runner_args, config)
        _ = _prepare_cache_behavior(spec, runner_args, config)

        if spec.parser_spec:
            module = core._load_parser_module(spec.parser_spec)
        else:
            module = core._load_parser_module(None)
        core._set_parser_module(module)

        state = core.load_state(layout.state_file, core.classify_document_type)

        entries_total = sum(1 for entry in state.entries.values() if isinstance(entry, dict))
        documents_total = 0
        downloaded_total = 0
        entries_without_documents = 0
        for entry in state.entries.values():
            documents = [doc for doc in entry.get("documents", []) if isinstance(doc, dict)]
            if not documents:
                entries_without_documents += 1
            documents_total += len(documents)
            downloaded_total += sum(1 for doc in documents if doc.get("downloaded"))

        pending_total = max(0, documents_total - downloaded_total)

        tracked_files = sum(1 for record in state.files.values() if isinstance(record, dict))
        tracked_downloaded = sum(
            1
            for record in state.files.values()
            if isinstance(record, dict) and record.get("downloaded")
        )

        state_last_updated = _safe_mtime(layout.state_file)
        page_cache_dir = layout.pages_dir
        pages_cached = _count_pages(page_cache_dir)
        cache_path = None
        if spec.start_url:
            cache_path = build_cache_path_for_url(page_cache_dir, spec.start_url)
        page_cache_last_fetch = _safe_mtime(cache_path)
        page_cache_fresh = core._listing_cache_is_fresh(page_cache_dir, spec.start_url)

        output_dir = layout.output_dir
        output_files = _count_files(output_dir)
        output_size_bytes = _sum_file_sizes(output_dir)

        next_run_earliest: Optional[datetime] = None
        next_run_latest: Optional[datetime] = None
        if state_last_updated is not None:
            next_run_earliest = state_last_updated + timedelta(hours=http_options.min_hours)
            next_run_latest = state_last_updated + timedelta(hours=http_options.max_hours)

        status, reason = _compute_status(entries_total, pending_total, page_cache_fresh, pages_cached)

        overview = TaskOverview(
            name=spec.name,
            start_url=spec.start_url,
            entries_total=entries_total,
            documents_total=documents_total,
            downloaded_total=downloaded_total,
            pending_total=pending_total,
            entries_without_documents=entries_without_documents,
            tracked_files=tracked_files,
            tracked_downloaded=tracked_downloaded,
            document_type_counts=_document_type_counts(state),
            state_file=layout.state_file,
            state_last_updated=state_last_updated,
            output_dir=output_dir,
            output_files=output_files,
            output_size_bytes=output_size_bytes,
            page_cache_dir=page_cache_dir,
            pages_cached=pages_cached,
            page_cache_fresh=page_cache_fresh,
            page_cache_last_fetch=page_cache_last_fetch,
            delay=http_options.delay,
            jitter=http_options.jitter,
            timeout=http_options.timeout,
            min_hours=http_options.min_hours,
            max_hours=http_options.max_hours,
            next_run_earliest=next_run_earliest,
            next_run_latest=next_run_latest,
            status=status,
            status_reason=reason,
            parser_spec=spec.parser_spec,
        )
        overviews.append(overview)

    return overviews


def _load_index_template() -> str:
    if not WEB_DIR.exists():
        raise FileNotFoundError(
            "The web directory does not exist. Expected frontend assets in 'web/'."
        )
    template_path = WEB_DIR / "index.html"
    if not template_path.is_file():
        raise FileNotFoundError(
            "The dashboard front-end template 'web/index.html' was not found."
        )
    return template_path.read_text(encoding="utf-8")


@functools.lru_cache(maxsize=1)
def _cached_index_template() -> str:
    return _load_index_template()


def _render_index_html(
    *,
    auto_refresh: Optional[int],
    generated_at: datetime,
    initial_data: Optional[Iterable[TaskOverview]] = None,
    static_snapshot: bool = False,
    api_base: str = "",
    search_config: Optional[Dict[str, object]] = None,
) -> str:
    template = _cached_index_template()
    config: Dict[str, object] = {
        "autoRefresh": auto_refresh if auto_refresh and auto_refresh > 0 else None,
        "generatedAt": generated_at.isoformat(timespec="seconds"),
        "staticSnapshot": static_snapshot,
        "apiBase": api_base,
    }
    if initial_data is not None:
        config["initialData"] = [overview.to_jsonable() for overview in initial_data]
    if search_config is not None:
        config["search"] = search_config

    config_script = (
        "<script>window.__PBC_CONFIG__ = "
        + json.dumps(config, ensure_ascii=False)
        + "</script>"
    )
    return template.replace("<!--CONFIG_PLACEHOLDER-->", config_script)


def render_dashboard_html(
    overviews: Iterable[TaskOverview],
    *,
    generated_at: Optional[datetime] = None,
    auto_refresh: Optional[int] = 30,
    search_config: Optional[Dict[str, object]] = None,
) -> str:
    """Render a standalone HTML snapshot of the dashboard."""

    generated_at = generated_at or datetime.now()
    return _render_index_html(
        auto_refresh=auto_refresh,
        generated_at=generated_at,
        initial_data=list(overviews),
        static_snapshot=True,
        search_config=search_config
        if search_config is not None
        else {"enabled": False, "reason": "Search is unavailable in static snapshots."},
    )


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

def _serve_dashboard(
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
    overviews_lock = threading.Lock()

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

    class DashboardHandler(BaseHTTPRequestHandler):
        search_finder = policy_finder
        search_default_topk = search_default_topk
        search_max_topk = search_max_topk
        search_include_documents = search_include_documents
        search_reason = search_reason
        search_config_payload = search_config_payload

        def _write(
            self,
            content: bytes,
            content_type: str = "text/html; charset=utf-8",
            *,
            status: HTTPStatus = HTTPStatus.OK,
            extra_headers: Optional[Dict[str, str]] = None,
        ) -> None:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(content)))
            if extra_headers:
                for key, value in extra_headers.items():
                    self.send_header(key, value)
            self.end_headers()
            self.wfile.write(content)

        def _json_response(
            self, payload: object, *, status: HTTPStatus = HTTPStatus.OK
        ) -> None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            headers = {"Access-Control-Allow-Origin": "*"}
            self._write(
                body,
                "application/json; charset=utf-8",
                status=status,
                extra_headers=headers,
            )

        def _serve_static(self, path: str) -> None:
            relative = path.lstrip("/")
            if not relative:
                relative = "index.html"
            base_dir = WEB_DIR.resolve()
            try:
                target = (base_dir / relative).resolve()
                target.relative_to(base_dir)
            except ValueError:
                self.send_error(HTTPStatus.NOT_FOUND, "File not found")
                return
            if not target.is_file():
                self.send_error(HTTPStatus.NOT_FOUND, "File not found")
                return
            content_type = mimetypes.guess_type(str(target))[0] or "application/octet-stream"
            data = target.read_bytes()
            if content_type.startswith("text/") or content_type in {"application/javascript", "application/json"}:
                content_type = f"{content_type}; charset=utf-8"
            self._write(data, content_type)

        def _search_disabled_response(self) -> None:
            payload: Dict[str, object] = {"error": "search_disabled"}
            if isinstance(self.search_reason, str):
                payload["reason"] = self.search_reason
            self._json_response(payload, status=HTTPStatus.NOT_FOUND)

        def _handle_search(self, query: str, topk: int, include_documents: bool) -> None:
            if self.search_finder is None:
                self._search_disabled_response()
                return
            results = [
                _search_entry_payload(entry, score, include_documents)
                for entry, score in self.search_finder.search(query, topk=topk)
            ]
            self._json_response(
                {
                    "query": query,
                    "topk": topk,
                    "include_documents": include_documents,
                    "result_count": len(results),
                    "results": results,
                }
            )

        def do_OPTIONS(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler interface
            parsed = urlsplit(self.path)
            if parsed.path == "/api/search":
                self.send_response(HTTPStatus.NO_CONTENT)
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
                self.send_header("Access-Control-Allow-Headers", "Content-Type")
                self.end_headers()
                return
            self.send_response(HTTPStatus.NOT_FOUND)
            self.end_headers()

        def do_GET(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler interface
            parsed = urlsplit(self.path)
            path = parsed.path or "/"
            if path == "/api/tasks":
                try:
                    with overviews_lock:
                        overviews = collect_task_overviews(
                            config_path,
                            task=task,
                            artifact_dir_override=artifact_dir_override,
                        )
                    payload = [overview.to_jsonable() for overview in overviews]
                    self._json_response(payload)
                except Exception as exc:  # pragma: no cover - logged to client
                    self._json_response(
                        {"error": str(exc)},
                        status=HTTPStatus.INTERNAL_SERVER_ERROR,
                    )
                return

            if path == "/healthz":
                self._write(b"ok", "text/plain; charset=utf-8")
                return

            if path == "/api/search":
                if self.search_finder is None:
                    self._search_disabled_response()
                    return
                params = parse_qs(parsed.query or "")
                query_values = params.get("query") or params.get("q")
                if not query_values or not query_values[0].strip():
                    self._json_response(
                        {"error": "missing_query"},
                        status=HTTPStatus.BAD_REQUEST,
                    )
                    return
                query = query_values[0].strip()
                topk_param = params.get("topk", [None])[0]
                try:
                    topk = _coerce_search_topk(
                        topk_param,
                        default=self.search_default_topk,
                        limit=self.search_max_topk,
                    )
                except Exception:
                    self._json_response(
                        {"error": "invalid_topk"},
                        status=HTTPStatus.BAD_REQUEST,
                    )
                    return

                include_documents = self.search_include_documents
                include_param = params.get("include_documents") or params.get("documents")
                if include_param and include_param[0] is not None:
                    try:
                        parsed_bool = _coerce_search_bool(include_param[0])
                    except Exception:
                        self._json_response(
                            {"error": "invalid_include_documents"},
                            status=HTTPStatus.BAD_REQUEST,
                        )
                        return
                    if parsed_bool is not None:
                        include_documents = parsed_bool

                self._handle_search(query, topk, include_documents)
                return

            if path in ("/", "/index.html"):
                try:
                    html = _render_index_html(
                        auto_refresh=auto_refresh,
                        generated_at=datetime.now(),
                        api_base="",
                        search_config=self.search_config_payload,
                    ).encode("utf-8")
                except FileNotFoundError as exc:  # pragma: no cover - configuration issue
                    message = f"Dashboard error: {exc}".encode("utf-8")
                    self.send_response(HTTPStatus.INTERNAL_SERVER_ERROR)
                    self.send_header("Content-Type", "text/plain; charset=utf-8")
                    self.send_header("Content-Length", str(len(message)))
                    self.end_headers()
                    self.wfile.write(message)
                    return
                self._write(html)
                return

            self._serve_static(path)

        def do_POST(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler interface
            parsed = urlsplit(self.path)
            if parsed.path != "/api/search":
                self._json_response({"error": "not_found"}, status=HTTPStatus.NOT_FOUND)
                return

            if self.search_finder is None:
                self._search_disabled_response()
                return

            content_length = self.headers.get("Content-Length")
            try:
                length = int(content_length) if content_length else 0
            except ValueError:
                self._json_response(
                    {"error": "invalid_content_length"},
                    status=HTTPStatus.BAD_REQUEST,
                )
                return

            data = self.rfile.read(length) if length > 0 else b""
            if not data:
                self._json_response(
                    {"error": "empty_body"},
                    status=HTTPStatus.BAD_REQUEST,
                )
                return

            try:
                payload = json.loads(data.decode("utf-8"))
            except json.JSONDecodeError:
                self._json_response(
                    {"error": "invalid_json"},
                    status=HTTPStatus.BAD_REQUEST,
                )
                return

            query = payload.get("query") or payload.get("q")
            if not isinstance(query, str) or not query.strip():
                self._json_response(
                    {"error": "missing_query"},
                    status=HTTPStatus.BAD_REQUEST,
                )
                return
            query = query.strip()

            try:
                topk = _coerce_search_topk(
                    payload.get("topk"),
                    default=self.search_default_topk,
                    limit=self.search_max_topk,
                )
            except Exception:
                self._json_response(
                    {"error": "invalid_topk"},
                    status=HTTPStatus.BAD_REQUEST,
                )
                return

            include_documents = self.search_include_documents
            if "include_documents" in payload:
                try:
                    parsed_bool = _coerce_search_bool(payload.get("include_documents"))
                except Exception:
                    self._json_response(
                        {"error": "invalid_include_documents"},
                        status=HTTPStatus.BAD_REQUEST,
                    )
                    return
                if parsed_bool is not None:
                    include_documents = parsed_bool

            self._handle_search(query, topk, include_documents)

        def log_message(self, format: str, *args: object) -> None:  # noqa: A003 - BaseHTTPRequestHandler signature
            sys.stderr.write(
                "%s - - [%s] %s\n"
                % (self.address_string(), self.log_date_time_string(), format % args)
            )

    with HTTPServer((host, port), DashboardHandler) as httpd:
        address = httpd.server_address
        host_display = address[0]
        if host_display == "0.0.0.0":
            host_display = socket.gethostbyname(socket.gethostname())
        print(
            f"Serving dashboard on http://{host_display}:{address[1]} (Ctrl+C to quit)",
            file=sys.stderr,
        )
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:  # pragma: no cover - manual stop
            print("Stopping dashboard", file=sys.stderr)


def main(argv: Optional[List[str]] = None) -> None:
    parser = argparse.ArgumentParser(description="Run the PBC monitor dashboard")
    parser.add_argument("--config", default="pbc_config.json", help="Path to config file")
    parser.add_argument("--artifact-dir", help="Override artifact directory")
    parser.add_argument("--task", help="Only show a specific task by name")
    parser.add_argument("--host", default="0.0.0.0", help="Dashboard bind host")
    parser.add_argument("--port", type=int, default=8000, help="Dashboard port")
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
        html = render_dashboard_html(overviews, generated_at=datetime.now(), auto_refresh=args.refresh)
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
        print(f"[dashboard] Search interface disabled: {search_error}", file=sys.stderr)

    _serve_dashboard(
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

