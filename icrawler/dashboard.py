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
from typing import Dict, Iterable, List, Optional
from urllib.parse import urlsplit

from . import pbc_monitor as core
from .fetching import build_cache_path_for_url
from .runner import (
    _build_tasks,
    _prepare_cache_behavior,
    _prepare_http_options,
    _prepare_task_layout,
)
from .state import PBCState


WEB_DIR = Path(__file__).resolve().parent.parent / "web"


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
) -> str:
    """Render a standalone HTML snapshot of the dashboard."""

    generated_at = generated_at or datetime.now()
    return _render_index_html(
        auto_refresh=auto_refresh,
        generated_at=generated_at,
        initial_data=list(overviews),
        static_snapshot=True,
    )

def _serve_dashboard(
    config_path: str,
    host: str,
    port: int,
    *,
    auto_refresh: int,
    task: Optional[str],
    artifact_dir_override: Optional[str],
) -> None:
    overviews_lock = threading.Lock()

    class DashboardHandler(BaseHTTPRequestHandler):
        def _write(self, content: bytes, content_type: str = "text/html; charset=utf-8") -> None:
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)

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
                    payload = json.dumps(
                        [overview.to_jsonable() for overview in overviews],
                        ensure_ascii=False,
                        indent=2,
                    ).encode("utf-8")
                    self._write(payload, "application/json; charset=utf-8")
                except Exception as exc:  # pragma: no cover - logged to client
                    message = json.dumps({"error": str(exc)}).encode("utf-8")
                    self.send_response(HTTPStatus.INTERNAL_SERVER_ERROR)
                    self.send_header("Content-Type", "application/json; charset=utf-8")
                    self.send_header("Content-Length", str(len(message)))
                    self.end_headers()
                    self.wfile.write(message)
                return

            if path == "/healthz":
                self._write(b"ok", "text/plain; charset=utf-8")
                return

            if path in ("/", "/index.html"):
                try:
                    html = _render_index_html(
                        auto_refresh=auto_refresh,
                        generated_at=datetime.now(),
                        api_base="",
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

    _serve_dashboard(
        config_path,
        args.host,
        args.port,
        auto_refresh=args.refresh,
        task=args.task,
        artifact_dir_override=args.artifact_dir,
    )


if __name__ == "__main__":
    main()

