from __future__ import annotations

import argparse
import functools
import json
import os
import socket
import sys
import threading
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from . import pbc_monitor as core
from .crawler import safe_filename
from .fetching import build_cache_path_for_url
from .runner import (
    _build_tasks,
    _prepare_cache_behavior,
    _prepare_http_options,
    _prepare_task_layout,
)
from .state import PBCState

try:  # pragma: no cover - optional dependency during import
    from fastapi import FastAPI, HTTPException, Request
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, PlainTextResponse
    import uvicorn
except ImportError as exc:  # pragma: no cover - optional dependency during import
    FastAPI = None  # type: ignore[assignment]
    HTTPException = None  # type: ignore[assignment]
    Request = None  # type: ignore[assignment]
    CORSMiddleware = None  # type: ignore[assignment]
    FileResponse = None  # type: ignore[assignment]
    HTMLResponse = None  # type: ignore[assignment]
    JSONResponse = None  # type: ignore[assignment]
    PlainTextResponse = None  # type: ignore[assignment]
    uvicorn = None  # type: ignore[assignment]
    _FASTAPI_IMPORT_ERROR = exc
else:
    _FASTAPI_IMPORT_ERROR = None


WEB_DIR = Path(__file__).resolve().parent.parent / "web"


@dataclass
class TaskOverview:
    name: str
    slug: str
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
    entries: Optional[List[Dict[str, object]]] = None

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
        if self.entries is None:
            data.pop("entries", None)
        return data


def _make_task_slug(name: str, counts: Dict[str, int]) -> str:
    base = safe_filename(name) or "task"
    counts[base] += 1
    if counts[base] > 1:
        return f"{base}-{counts[base]}"
    return base


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
    include_entries: bool = False,
) -> List[TaskOverview]:
    config = _load_config(config_path)
    if artifact_dir_override:
        config["artifact_dir"] = artifact_dir_override
    artifact_dir = str(config.get("artifact_dir") or ".")
    runner_args = _default_runner_args(task)
    tasks = _build_tasks(runner_args, config, artifact_dir)
    overviews: List[TaskOverview] = []
    slug_counts: Dict[str, int] = defaultdict(int)

    for spec in tasks:
        slug = _make_task_slug(spec.name, slug_counts)
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

        entries_payload: Optional[List[Dict[str, object]]] = None
        if include_entries:
            jsonable = state.to_jsonable()
            entries = jsonable.get("entries") if isinstance(jsonable, dict) else None
            if isinstance(entries, list):
                entries_payload = entries

        overview = TaskOverview(
            name=spec.name,
            slug=slug,
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
            entries=entries_payload,
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
    default_search_config = (
        search_config
        if search_config is not None
        else {
            "enabled": False,
            "reason": "Search is available from the combined portal via `python -m icrawler`.",
        }
    )
    return _render_index_html(
        auto_refresh=auto_refresh,
        generated_at=generated_at,
        initial_data=list(overviews),
        static_snapshot=True,
        search_config=default_search_config,
    )


def create_dashboard_app(
    config_path: str,
    *,
    auto_refresh: int,
    task: Optional[str],
    artifact_dir_override: Optional[str],
    search_config: Optional[Dict[str, object]] = None,
):
    if (
        FastAPI is None
        or uvicorn is None
        or JSONResponse is None
        or HTMLResponse is None
        or PlainTextResponse is None
        or FileResponse is None
        or CORSMiddleware is None
        or HTTPException is None
        or Request is None
    ):
        raise RuntimeError(
            "FastAPI and uvicorn are required to run the dashboard. "
            "Install them via `pip install fastapi uvicorn`."
        ) from _FASTAPI_IMPORT_ERROR

    overviews_lock = threading.Lock()

    search_payload: Dict[str, object] = (
        dict(search_config) if isinstance(search_config, dict) else {"enabled": False}
    )

    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/api/tasks")
    def get_tasks() -> JSONResponse:
        try:
            with overviews_lock:
                overviews = collect_task_overviews(
                    config_path,
                    task=task,
                    artifact_dir_override=artifact_dir_override,
                )
            payload = [overview.to_jsonable() for overview in overviews]
            return JSONResponse(payload)
        except Exception as exc:  # pragma: no cover - logged to client
            return JSONResponse({"error": str(exc)}, status_code=500)

    @app.get("/api/tasks/{slug}/entries")
    def get_task_entries(slug: str) -> JSONResponse:
        try:
            with overviews_lock:
                overviews = collect_task_overviews(
                    config_path,
                    task=task,
                    artifact_dir_override=artifact_dir_override,
                )
            overview = next((item for item in overviews if item.slug == slug), None)
            if overview is None:
                raise HTTPException(status_code=404, detail="Task not found")
            if not overview.state_file:
                return JSONResponse({"entries": [], "task": overview.to_jsonable()})
            if overview.parser_spec:
                module = core._load_parser_module(overview.parser_spec)
            else:
                module = core._load_parser_module(None)
            core._set_parser_module(module)
            state = core.load_state(overview.state_file, core.classify_document_type)
            jsonable = state.to_jsonable()
            entries = jsonable.get("entries") if isinstance(jsonable, dict) else None
            payload = {
                "entries": entries if isinstance(entries, list) else [],
                "task": overview.to_jsonable(),
            }
            return JSONResponse(payload)
        except HTTPException:
            raise
        except Exception as exc:  # pragma: no cover - logged to client
            return JSONResponse({"error": str(exc)}, status_code=500)

    @app.get("/healthz")
    def healthcheck() -> PlainTextResponse:
        return PlainTextResponse("ok")

    def _render_index_response() -> HTMLResponse:
        try:
            html = _render_index_html(
                auto_refresh=auto_refresh,
                generated_at=datetime.now(),
                api_base="",
                search_config=search_payload,
            )
        except FileNotFoundError as exc:  # pragma: no cover - configuration issue
            message = f"Dashboard error: {exc}"
            return HTMLResponse(message, status_code=500)
        return HTMLResponse(html)

    @app.get("/")
    def index() -> HTMLResponse:
        return _render_index_response()

    @app.get("/index.html")
    def index_html() -> HTMLResponse:
        return _render_index_response()

    @app.get("/{resource_path:path}", include_in_schema=False)
    def serve_static(resource_path: str) -> FileResponse:
        relative = resource_path.lstrip("/")
        if not relative:
            relative = "index.html"
        base_dir = WEB_DIR.resolve()
        try:
            target = (base_dir / relative).resolve()
            target.relative_to(base_dir)
        except ValueError:
            raise HTTPException(status_code=404, detail="File not found")
        if not target.is_file():
            raise HTTPException(status_code=404, detail="File not found")
        return FileResponse(target)

    return app


def _serve_dashboard(
    config_path: str,
    host: str,
    port: int,
    *,
    auto_refresh: int,
    task: Optional[str],
    artifact_dir_override: Optional[str],
    search_config: Optional[Dict[str, object]] = None,
) -> None:
    app = create_dashboard_app(
        config_path,
        auto_refresh=auto_refresh,
        task=task,
        artifact_dir_override=artifact_dir_override,
        search_config=search_config,
    )

    host_display = host
    if host_display == "0.0.0.0":
        try:
            host_display = socket.gethostbyname(socket.gethostname())
        except OSError:  # pragma: no cover - best effort resolution
            host_display = host
    print(
        f"Serving dashboard on http://{host_display}:{port} (Ctrl+C to quit)",
        file=sys.stderr,
    )

    if uvicorn is None:  # pragma: no cover - safety check
        raise RuntimeError(
            "uvicorn is required to run the dashboard. Install it via `pip install uvicorn`."
        )

    uvicorn.run(app, host=host, port=port, log_level="info")


def main(argv: Optional[List[str]] = None) -> None:
    parser = argparse.ArgumentParser(description="Run the PBC monitor dashboard")
    parser.add_argument("--config", default="pbc_config.json", help="Path to config file")
    parser.add_argument("--artifact-dir", help="Override artifact directory")
    parser.add_argument("--task", help="Only show a specific task by name")
    parser.add_argument("--host", default="0.0.0.0", help="Dashboard bind host")
    parser.add_argument("--port", type=int, default=8000, help="Dashboard port")
    parser.add_argument("--refresh", type=int, default=30, help="Auto-refresh interval in seconds (set 0 to disable)")
    parser.add_argument("--once", action="store_true", help="Render the dashboard once to stdout and exit")
    parser.add_argument("--json", action="store_true", help="Output the collected overview as JSON and exit")

    args = parser.parse_args(argv)

    config_path = args.config

    overviews = collect_task_overviews(
        config_path,
        task=args.task,
        artifact_dir_override=args.artifact_dir,
        include_entries=args.once,
    )

    disabled_search_config = {
        "enabled": False,
        "reason": "Search is available from the combined portal via `python -m icrawler`.",
    }

    if args.once and args.json:
        print(json.dumps([overview.to_jsonable() for overview in overviews], ensure_ascii=False, indent=2))
        return
    if args.once:
        html = render_dashboard_html(
            overviews,
            generated_at=datetime.now(),
            auto_refresh=args.refresh,
            search_config=disabled_search_config,
        )
        print(html)
        return
    if args.json:
        print(json.dumps([overview.to_jsonable() for overview in overviews], ensure_ascii=False, indent=2))
        return

    _serve_dashboard(
        config_path,
        args.host,
        args.port,
        auto_refresh=args.refresh,
        task=args.task,
        artifact_dir_override=args.artifact_dir,
        search_config=disabled_search_config,
    )


if __name__ == "__main__":
    main()

