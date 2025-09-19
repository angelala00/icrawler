from __future__ import annotations

import argparse
import importlib
import json
import logging
import os
import random
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from .crawler import safe_filename
from .fetcher import DEFAULT_HEADERS, get as http_get, sleep_with_jitter
from .parser import classify_document_type as _default_classify_document_type


logger = logging.getLogger(__name__)

DEFAULT_PARSER_SPEC = "icrawler.parser"
_current_parser_module: ModuleType = importlib.import_module(DEFAULT_PARSER_SPEC)


def _create_session() -> requests.Session:
    """Return a requests-like session with default headers applied."""

    session_factory = getattr(requests, "Session", None)
    session: Optional[requests.Session]
    if callable(session_factory):
        try:
            session = session_factory()
        except Exception as exc:  # pragma: no cover - defensive logging
            logger.debug("Failed to create requests session: %s", exc)
            session = None
    else:
        session = None

    if session is None:
        logger.debug("Falling back to simple session stub")
        session = SimpleNamespace(headers={}, close=lambda: None)
        get_callable = getattr(requests, "get", None)
        if callable(get_callable):
            setattr(session, "get", get_callable)

    headers = getattr(session, "headers", None)
    if isinstance(headers, dict):
        headers.update(DEFAULT_HEADERS)
    else:
        setattr(session, "headers", dict(DEFAULT_HEADERS))
    return session  # type: ignore[return-value]


def _load_parser_module(spec: Optional[str]) -> ModuleType:
    if not spec:
        return importlib.import_module(DEFAULT_PARSER_SPEC)
    return importlib.import_module(spec)


def _set_parser_module(module: ModuleType) -> None:
    global _current_parser_module
    _current_parser_module = module


def _parser_call(name: str):
    return getattr(_current_parser_module, name)


def extract_listing_entries(
    page_url: str,
    soup: BeautifulSoup,
    suffixes: Optional[Sequence[str]] = None,
) -> List[Dict[str, object]]:
    func = _parser_call("extract_listing_entries")
    if suffixes is None:
        return func(page_url, soup)
    return func(page_url, soup, suffixes)


def extract_file_links(
    page_url: str,
    soup: BeautifulSoup,
    suffixes: Optional[Sequence[str]] = None,
) -> List[Tuple[str, str]]:
    func = _parser_call("extract_file_links")
    if suffixes is None:
        links = func(page_url, soup)
    else:
        links = func(page_url, soup, suffixes)

    def _is_filename_title(title: str, file_url: str) -> bool:
        if not title:
            return True
        parsed = urlparse(file_url)
        basename = os.path.basename(parsed.path or "")
        if not basename:
            return False
        return title.strip().lower() == basename.lower()

    def _find_anchor_text(target_url: str) -> Optional[str]:
        for anchor in soup.find_all("a", href=True):
            href = (anchor.get("href") or "").strip()
            if not href:
                continue
            resolved = urljoin(page_url, href)
            if resolved != target_url:
                continue
            title_attr = (anchor.get("title") or "").strip()
            if title_attr:
                return title_attr
            text = anchor.get_text(" ", strip=True)
            if text:
                return text
        return None

    cleaned: List[Tuple[str, str]] = []
    for file_url, display_name in links:
        title = display_name if isinstance(display_name, str) else ""
        if _is_filename_title(title, file_url):
            anchor_text = _find_anchor_text(file_url)
            if anchor_text:
                title = anchor_text
        cleaned.append((file_url, title))
    return cleaned


def extract_pagination_links(
    current_url: str,
    soup: BeautifulSoup,
    start_url: str,
) -> List[str]:
    func = _parser_call("extract_pagination_links")
    return func(current_url, soup, start_url)


def snapshot_entries(html: str, base_url: str) -> Dict[str, object]:
    func = _parser_call("snapshot_entries")
    return func(html, base_url)


def _parser_snapshot_local_file(
    path: str, base_url: Optional[str] = None
) -> Dict[str, object]:
    func = _parser_call("snapshot_local_file")
    if base_url is None:
        return func(path)
    return func(path, base_url)


def extract_pagination_meta(
    page_url: str,
    soup: BeautifulSoup,
    start_url: str,
) -> Dict[str, object]:
    func = _parser_call("extract_pagination_meta")
    return func(page_url, soup, start_url)


def classify_document_type(url: str) -> str:
    func = getattr(_current_parser_module, "classify_document_type", None)
    if callable(func):
        return func(url)
    return _default_classify_document_type(url)


@dataclass
class TaskSpec:
    name: str
    start_url: str
    output_dir: str
    state_file: Optional[str]
    parser_spec: Optional[str]
    allowed_types: Optional[Set[str]]
    verify_local: bool
    raw_config: Dict[str, Any]
    from_task_list: bool


def _select_task_value(
    cli_value: Optional[Any],
    task_config: Optional[Dict[str, Any]],
    global_config: Optional[Dict[str, Any]],
    key: str,
    default: Optional[Any] = None,
) -> Optional[Any]:
    if cli_value is not None:
        return cli_value
    if task_config and key in task_config:
        return task_config[key]
    if global_config and key in global_config:
        return global_config[key]
    return default


def _normalize_download_types(value: Optional[Any]) -> Optional[Set[str]]:
    if value is None:
        return None
    if isinstance(value, str):
        value = [value]
    try:
        return {str(item).lower() for item in value}
    except TypeError:
        return None


def _build_tasks(
    args: argparse.Namespace,
    config: Dict[str, Any],
    artifact_dir: str,
) -> List[TaskSpec]:
    tasks_config = config.get("tasks")

    # If CLI positional overrides are provided, treat as single ad-hoc task.
    if args.start_url or args.output_dir:
        start_url_value = _select_task_value(args.start_url, None, config, "start_url")
        start_url_str = str(start_url_value) if start_url_value is not None else ""
        output_dir = _select_task_value(args.output_dir, None, config, "output_dir")
        parser_spec = _select_task_value(None, None, config, "parser")
        download_types = _normalize_download_types(
            _select_task_value(None, None, config, "download_types")
        )
        if args.verify_local:
            verify_local = True
        else:
            verify_local = bool(config.get("verify_local", False))
        state_file = _select_task_value(args.state_file, None, config, "state_file", "state.json")
        name = args.task or "default"
        task = TaskSpec(
            name=name,
            start_url=start_url_str,
            output_dir=str(output_dir) if output_dir else "",
            state_file=state_file,
            parser_spec=parser_spec,
            allowed_types=download_types,
            verify_local=verify_local,
            raw_config={},
            from_task_list=False,
        )
        logger.info(
            "Prepared CLI override task '%s' with start URL %s",
            task.name,
            task.start_url,
        )
        return [task]

    task_specs: List[TaskSpec] = []

    if isinstance(tasks_config, list) and tasks_config:
        for index, raw_task in enumerate(tasks_config):
            if not isinstance(raw_task, dict):
                continue
            name = str(raw_task.get("name") or f"task{index + 1}")
            if args.task and args.task != name:
                continue
            start_url_value = _select_task_value(None, raw_task, config, "start_url")
            start_url_str = str(start_url_value) if start_url_value is not None else ""
            output_dir = _select_task_value(None, raw_task, config, "output_dir")
            parser_spec = _select_task_value(None, raw_task, config, "parser")
            download_types = _normalize_download_types(
                _select_task_value(None, raw_task, config, "download_types")
            )
            task_verify = raw_task.get("verify_local")
            if args.verify_local:
                verify_local = True
            elif task_verify is not None:
                verify_local = bool(task_verify)
            else:
                verify_local = bool(config.get("verify_local", False))
            state_file = _select_task_value(None, raw_task, config, "state_file", "state.json")
            task_specs.append(
                TaskSpec(
                    name=name,
                    start_url=start_url_str,
                    output_dir=str(output_dir) if output_dir else "",
                    state_file=state_file,
                    parser_spec=parser_spec,
                    allowed_types=download_types,
                    verify_local=verify_local,
                    raw_config=raw_task,
                    from_task_list=True,
                )
            )
        if args.task and not task_specs:
            raise SystemExit(f"Task '{args.task}' not found in configuration")
        if task_specs:
            logger.info(
                "Prepared %d configured task(s): %s",
                len(task_specs),
                ", ".join(spec.name for spec in task_specs),
            )
            return task_specs

    # Fallback to single-task configuration.
    start_url_value = _select_task_value(args.start_url, None, config, "start_url")
    start_url_str = str(start_url_value) if start_url_value is not None else ""
    output_dir = _select_task_value(args.output_dir, None, config, "output_dir")
    parser_spec = _select_task_value(None, None, config, "parser")
    download_types = _normalize_download_types(config.get("download_types"))
    if args.verify_local:
        verify_local = True
    else:
        verify_local = bool(config.get("verify_local", False))
    state_file = _select_task_value(args.state_file, None, config, "state_file", "state.json")
    name = args.task or "default"
    task = TaskSpec(
        name=name,
        start_url=start_url_str,
        output_dir=str(output_dir) if output_dir else "",
        state_file=state_file,
        parser_spec=parser_spec,
        allowed_types=download_types,
        verify_local=verify_local,
        raw_config=config,
        from_task_list=False,
    )
    logger.info(
        "Prepared default task '%s' with start URL %s",
        task.name,
        task.start_url,
    )
    return [task]


def _run_task(
    task: TaskSpec,
    args: argparse.Namespace,
    config: Dict[str, Any],
    artifact_dir: str,
) -> None:

    parser_module = _load_parser_module(task.parser_spec)
    _set_parser_module(parser_module)

    pages_base = os.path.join(artifact_dir, "pages")
    if task.from_task_list:
        pages_dir = os.path.join(pages_base, safe_filename(task.name))
    else:
        pages_dir = pages_base

    state_value = task.state_file or "state.json"
    state_file = _normalize_output_path(
        str(state_value),
        artifact_dir,
        "state",
        task.name if task.from_task_list else None,
    )

    dump_value = _select_task_value(
        args.dump_structure,
        task.raw_config,
        config,
        "dump_structure",
    )
    dump_target = _normalize_output_path(
        dump_value,
        artifact_dir,
        "structure",
        task.name if task.from_task_list else None,
    ) if dump_value else None

    download_value = _select_task_value(
        args.download_from_structure,
        task.raw_config,
        config,
        "download_from_structure",
    )
    download_target = _normalize_output_path(
        download_value,
        artifact_dir,
        "structure",
        task.name if task.from_task_list else None,
    ) if download_value else None

    fetch_value = _select_task_value(
        args.fetch_page,
        task.raw_config,
        config,
        "fetch_page",
    )
    fetch_target = _normalize_output_path(
        fetch_value,
        artifact_dir,
        "pages",
        task.name if task.from_task_list else None,
    ) if fetch_value else None

    dump_from_file_value = _select_task_value(
        args.dump_from_file,
        task.raw_config,
        config,
        "dump_from_file",
    )
    dump_from_file = _normalize_output_path(
        dump_from_file_value,
        artifact_dir,
        "pages",
        task.name if task.from_task_list else None,
    ) if dump_from_file_value else None

    start_url = str(task.start_url) if task.start_url else ""
    output_value = task.output_dir if task.output_dir else None
    if output_value:
        output_dir = _normalize_output_path(
            output_value,
            artifact_dir,
            "downloads",
            task.name if task.from_task_list else None,
        )
    else:
        if task.from_task_list:
            default_segment = safe_filename(task.name) or "downloads"
            output_dir = os.path.join(artifact_dir, "downloads", default_segment)
        else:
            output_dir = os.path.join(artifact_dir, "downloads")

    logger.info(
        "Starting task '%s': start_url=%s, output_dir=%s, state_file=%s",
        task.name,
        start_url or "(none)",
        output_dir or "(none)",
        state_file or "(none)",
    )
    logger.info("Using page cache directory: %s", pages_dir)

    delay = float(_select_task_value(args.delay, task.raw_config, config, "delay", 3.0))
    jitter = float(_select_task_value(args.jitter, task.raw_config, config, "jitter", 2.0))
    timeout = float(_select_task_value(args.timeout, task.raw_config, config, "timeout", 30.0))
    min_hours = float(_select_task_value(args.min_hours, task.raw_config, config, "min_hours", 20.0))
    max_hours = float(_select_task_value(args.max_hours, task.raw_config, config, "max_hours", 32.0))

    allowed_types = task.allowed_types
    verify_local = task.verify_local

    logger.info(
        "HTTP options for task '%s': delay=%.2fs, jitter=%.2fs, timeout=%.2fs",
        task.name,
        delay,
        jitter,
        timeout,
    )
    if not args.run_once and not dump_target and not fetch_target and not dump_from_file and not download_target:
        logger.info(
            "Monitor sleep window: %.2f-%.2f hours",
            min_hours,
            max_hours,
        )
    if allowed_types:
        logger.info(
            "Allowed document types: %s",
            ", ".join(sorted(allowed_types)),
        )
    logger.info("Verify local files: %s", "enabled" if verify_local else "disabled")

    refresh_pages = bool(args.refresh_pages)
    use_cached_pages_flag = bool(args.use_cached_pages) and not refresh_pages
    prefetch_requested = bool(args.prefetch_pages)
    if prefetch_requested:
        if not start_url:
            raise SystemExit("start_url must be provided to prefetch listing pages")
        logger.info(
            "Prefetching listing pages for task '%s' into %s",
            task.name,
            pages_dir,
        )
        page_total = prefetch_listing_pages(
            str(start_url),
            delay,
            jitter,
            timeout,
            pages_dir,
        )
        logger.info(
            "Prefetch cached %d page(s) for task '%s'",
            page_total,
            task.name,
        )

    followup_requested = any(
        [
            dump_from_file,
            fetch_target,
            dump_target,
            download_target,
            args.run_once,
        ]
    )
    if prefetch_requested and not followup_requested:
        logger.info("Prefetch completed with no additional actions requested; exiting")
        return

    if not dump_from_file and not download_target and not start_url:
        raise SystemExit(f"start_url must be provided for task '{task.name}'")

    if (
        not fetch_target
        and not dump_target
        and not dump_from_file
        and not download_target
        and output_dir is None
    ):
        raise SystemExit(f"output_dir must be provided for task '{task.name}'")

    if dump_from_file:
        logger.info(
            "Dumping structure for task '%s' from local file %s",
            task.name,
            dump_from_file,
        )
        snapshot = snapshot_local_file(dump_from_file, start_url or None)
        print(json.dumps(snapshot, ensure_ascii=False, indent=2))
        return

    if fetch_target:
        if not start_url:
            raise SystemExit("start_url must be provided to fetch listing HTML")
        logger.info(
            "Fetching start page %s for task '%s' to %s",
            start_url,
            task.name,
            "stdout" if fetch_target == "-" else fetch_target,
        )
        html_content = fetch_listing_html(str(start_url), delay, jitter, timeout)
        if fetch_target == "-":
            print(html_content)
            logger.info("Fetched HTML written to stdout")
        else:
            os.makedirs(os.path.dirname(fetch_target), exist_ok=True)
            with open(str(fetch_target), "w", encoding="utf-8") as handle:
                handle.write(html_content)
            logger.info("Fetched HTML saved to %s", fetch_target)
        return

    if dump_target:
        if not start_url:
            raise SystemExit("start_url must be provided to dump listing structure")
        logger.info(
            "Dumping listing structure for task '%s' from %s to %s",
            task.name,
            start_url,
            "stdout" if dump_target == "-" else dump_target,
        )
        snapshot = snapshot_listing(
            str(start_url),
            delay,
            jitter,
            timeout,
            page_cache_dir=pages_dir,
            use_cache=use_cached_pages_flag,
            refresh_cache=refresh_pages,
        )
        if dump_target == "-":
            print(json.dumps(snapshot, ensure_ascii=False, indent=2))
            logger.info("Listing snapshot written to stdout")
        else:
            os.makedirs(os.path.dirname(dump_target), exist_ok=True)
            with open(str(dump_target), "w", encoding="utf-8") as handle:
                json.dump(snapshot, handle, ensure_ascii=False, indent=2)
            logger.info("Listing snapshot saved to %s", dump_target)
        return

    if download_target:
        if download_target == "-":
            raise SystemExit("--download-from-structure does not support '-' as input")
        if not os.path.exists(download_target):
            raise SystemExit(f"Structure file not found: {download_target}")
        if output_dir is None:
            raise SystemExit("output_dir must be provided to download attachments")
        logger.info(
            "Downloading attachments for task '%s' from %s into %s",
            task.name,
            download_target,
            output_dir,
        )
        download_from_structure(
            download_target,
            str(output_dir),
            state_file,
            delay,
            jitter,
            timeout,
            allowed_types,
            verify_local,
        )
        logger.info("Attachment download finished")
        return

    if args.run_once:
        if not start_url:
            raise SystemExit("start_url must be provided to run monitor")
        logger.info("Running single monitoring iteration for task '%s'", task.name)
        monitor_once(
            str(start_url),
            str(output_dir),
            state_file,
            delay,
            jitter,
            timeout,
            pages_dir,
            allowed_types,
            verify_local,
        )
    else:
        if not start_url:
            raise SystemExit("start_url must be provided to run monitor")
        logger.info(
            "Entering monitoring loop for task '%s' with sleep window %.2f-%.2f hours",
            task.name,
            min_hours,
            max_hours,
        )
        monitor_loop(
            str(start_url),
            str(output_dir),
            state_file,
            delay,
            jitter,
            timeout,
            min_hours,
            max_hours,
            pages_dir,
            allowed_types,
            verify_local,
        )


def _fetch(
    session: requests.Session,
    url: str,
    delay: float,
    jitter: float,
    timeout: float,
) -> str:
    response = http_get(
        url,
        session=session,
        delay=delay,
        jitter=jitter,
        timeout=timeout,
    )
    return response.text


def _sleep(delay: float, jitter: float) -> None:
    sleep_with_jitter(delay, jitter)


def iterate_listing_pages(
    session: requests.Session,
    start_url: str,
    delay: float,
    jitter: float,
    timeout: float,
    page_cache_dir: Optional[str] = None,
    *,
    use_cache: bool = False,
    refresh_cache: bool = False,
) -> Iterable[Tuple[str, BeautifulSoup, Optional[str]]]:
    queue: List[str] = [start_url]
    visited: Set[str] = set()
    while queue:
        url = queue.pop(0)
        if url in visited:
            continue
        html_path: Optional[str] = None
        cached_html: Optional[str] = None
        if page_cache_dir:
            os.makedirs(page_cache_dir, exist_ok=True)
            html_path = _cache_path_for_url(page_cache_dir, url)
            if (
                use_cache
                and not refresh_cache
                and os.path.exists(html_path)
            ):
                with open(html_path, "r", encoding="utf-8") as handle:
                    cached_html = handle.read()
                logger.info("Loaded cached listing page: %s", html_path)

        if cached_html is None:
            logger.info("Fetching listing page: %s", url)
            fetch_start = time.time()
            html = _fetch(session, url, delay, jitter, timeout)
            duration = time.time() - fetch_start
            logger.info(
                "Fetched listing page: %s (%.2f seconds, %d bytes)",
                url,
                duration,
                len(html),
            )
            if html_path:
                with open(html_path, "w", encoding="utf-8") as handle:
                    handle.write(html)
                logger.info("Cached listing page %s to %s", url, html_path)
            html_content = html
        else:
            html_content = cached_html
        soup = BeautifulSoup(html_content, "html.parser")
        yield url, soup, html_path
        visited.add(url)
        new_links: List[str] = []
        for link in extract_pagination_links(url, soup, start_url):
            if link not in visited and link not in queue and link not in new_links:
                queue.append(link)
                new_links.append(link)
        if new_links:
            logger.info(
                "Discovered %d pagination link(s) from %s",
                len(new_links),
                url,
            )
            logger.info("Pagination queue size is now %d", len(queue))

class PBCState:
    def __init__(self) -> None:
        self.entries: Dict[str, Dict[str, object]] = {}
        self.files: Dict[str, Dict[str, object]] = {}

    def _entry_id(self, entry: Dict[str, object]) -> str:
        documents = entry.get("documents") or []
        if isinstance(documents, list):
            for document in documents:
                if not isinstance(document, dict):
                    continue
                url_value = document.get("url")
                doc_type = document.get("type")
                if isinstance(url_value, str) and doc_type == "html":
                    return url_value
            for document in documents:
                if not isinstance(document, dict):
                    continue
                url_value = document.get("url")
                if isinstance(url_value, str) and url_value:
                    return url_value
        title = entry.get("title")
        remark = entry.get("remark")
        if isinstance(title, str) and title:
            key = f"title::{title}"
            if isinstance(remark, str) and remark:
                key = f"{key}::{remark}"
            return key
        serial = entry.get("serial")
        if isinstance(serial, int):
            return f"serial::{serial}"
        serialized = json.dumps(entry, ensure_ascii=False, sort_keys=True)
        return safe_filename(serialized)

    def ensure_entry(self, entry: Dict[str, object]) -> str:
        entry_id: Optional[str] = None
        documents = entry.get("documents")
        if isinstance(documents, list):
            for document in documents:
                if not isinstance(document, dict):
                    continue
                url_value = document.get("url")
                if not isinstance(url_value, str) or not url_value:
                    continue
                file_record = self.files.get(url_value)
                if isinstance(file_record, dict):
                    existing_id = file_record.get("entry_id")
                    if isinstance(existing_id, str) and existing_id in self.entries:
                        entry_id = existing_id
                        break
                for existing_id, existing_entry in self.entries.items():
                    documents_list = existing_entry.get("documents", [])
                    if not isinstance(documents_list, list):
                        continue
                    for existing_doc in documents_list:
                        if (
                            isinstance(existing_doc, dict)
                            and existing_doc.get("url") == url_value
                        ):
                            entry_id = existing_id
                            break
                    if entry_id is not None:
                        break
                if entry_id is not None:
                    break
        if entry_id is None:
            entry_id = self._entry_id(entry)
        existing = self.entries.get(entry_id)
        serial = entry.get("serial")
        title = entry.get("title")
        remark = entry.get("remark")
        if existing:
            if isinstance(serial, int):
                existing["serial"] = serial
            if isinstance(title, str):
                existing["title"] = title
            if isinstance(remark, str):
                existing["remark"] = remark
        else:
            self.entries[entry_id] = {
                "serial": serial if isinstance(serial, int) else None,
                "title": title if isinstance(title, str) else "",
                "remark": remark if isinstance(remark, str) else "",
                "documents": [],
            }
        return entry_id

    def merge_documents(self, entry_id: str, documents: Sequence[Dict[str, object]]) -> None:
        entry = self.entries.setdefault(entry_id, {"documents": []})
        existing_docs: Dict[str, Dict[str, object]] = {}
        for item in entry.get("documents", []):
            if isinstance(item, dict):
                url_value = item.get("url")
                if isinstance(url_value, str):
                    existing_docs[url_value] = item
        for document in documents:
            if not isinstance(document, dict):
                continue
            url_value = document.get("url")
            if not isinstance(url_value, str) or not url_value:
                continue
            doc_type = document.get("type")
            if not isinstance(doc_type, str) or not doc_type:
                doc_type = classify_document_type(url_value)
            title = document.get("title")
            if not isinstance(title, str):
                title = ""
            file_record = self.files.get(url_value)
            downloaded_flag = bool(document.get("downloaded"))
            if file_record and file_record.get("downloaded"):
                downloaded_flag = True
            local_path = document.get("local_path")
            if not isinstance(local_path, str):
                if file_record:
                    stored_path = file_record.get("local_path")
                    if isinstance(stored_path, str):
                        local_path = stored_path
                else:
                    local_path = None
            existing_doc = existing_docs.get(url_value)
            if existing_doc:
                existing_doc["type"] = doc_type
                if title:
                    existing_doc["title"] = title
                if downloaded_flag:
                    existing_doc["downloaded"] = True
                if local_path:
                    existing_doc["local_path"] = local_path
            else:
                new_doc: Dict[str, object] = {
                    "url": url_value,
                    "type": doc_type,
                    "title": title,
                }
                if downloaded_flag:
                    new_doc["downloaded"] = True
                if local_path:
                    new_doc["local_path"] = local_path
                entry.setdefault("documents", []).append(new_doc)
                existing_docs[url_value] = new_doc
            if file_record:
                if title:
                    file_record["title"] = title
                file_record["type"] = doc_type
                if downloaded_flag:
                    file_record["downloaded"] = True
                if local_path:
                    file_record["local_path"] = local_path
                file_record["entry_id"] = entry_id
            elif downloaded_flag:
                file_entry: Dict[str, object] = {
                    "entry_id": entry_id,
                    "title": title,
                    "type": doc_type,
                    "downloaded": True,
                }
                if local_path:
                    file_entry["local_path"] = local_path
                self.files[url_value] = file_entry

    def is_downloaded(self, url_value: str) -> bool:
        record = self.files.get(url_value)
        if not record:
            return False
        return bool(record.get("downloaded"))

    def mark_downloaded(
        self,
        entry_id: str,
        url_value: str,
        title: str,
        doc_type: str,
        local_path: Optional[str],
    ) -> None:
        file_entry = self.files.setdefault(url_value, {})
        file_entry["entry_id"] = entry_id
        file_entry["title"] = title
        file_entry["type"] = doc_type
        file_entry["downloaded"] = True
        if local_path:
            file_entry["local_path"] = local_path
        entry = self.entries.get(entry_id)
        if not entry:
            return
        for document in entry.get("documents", []):
            if not isinstance(document, dict):
                continue
            if document.get("url") == url_value:
                document["type"] = doc_type
                if title:
                    document["title"] = title
                document["downloaded"] = True
                if local_path:
                    document["local_path"] = local_path
                break
        else:
            new_doc: Dict[str, object] = {
                "url": url_value,
                "type": doc_type,
                "title": title,
                "downloaded": True,
            }
            if local_path:
                new_doc["local_path"] = local_path
            entry.setdefault("documents", []).append(new_doc)

    def clear_downloaded(self, url_value: str) -> None:
        file_record = self.files.get(url_value)
        if file_record:
            file_record["downloaded"] = False
            file_record.pop("local_path", None)
        for entry in self.entries.values():
            documents = entry.get("documents", [])
            if not isinstance(documents, list):
                continue
            for document in documents:
                if not isinstance(document, dict):
                    continue
                if document.get("url") == url_value:
                    document.pop("local_path", None)
                    if "downloaded" in document:
                        document.pop("downloaded", None)

    def update_document_title(self, url_value: str, title: str) -> None:
        if not title:
            return
        file_record = self.files.get(url_value)
        if file_record:
            file_record["title"] = title
        for entry in self.entries.values():
            for document in entry.get("documents", []):
                if isinstance(document, dict) and document.get("url") == url_value:
                    document["title"] = title

    def to_jsonable(self) -> Dict[str, object]:
        entries_list: List[Dict[str, object]] = []
        for entry in self.entries.values():
            documents: List[Dict[str, object]] = []
            for document in entry.get("documents", []):
                if not isinstance(document, dict):
                    continue
                doc_output: Dict[str, object] = {
                    "type": document.get("type"),
                    "url": document.get("url"),
                    "title": document.get("title", ""),
                }
                if document.get("downloaded"):
                    doc_output["downloaded"] = True
                local_path = document.get("local_path")
                if isinstance(local_path, str) and local_path:
                    doc_output["local_path"] = local_path
                documents.append(doc_output)
            entry_output: Dict[str, object] = {
                "serial": entry.get("serial"),
                "title": entry.get("title", ""),
                "remark": entry.get("remark", ""),
                "documents": documents,
            }
            entries_list.append(entry_output)
        entries_list.sort(
            key=lambda item: (
                item.get("serial") is None,
                item.get("serial") if isinstance(item.get("serial"), int) else 0,
                item.get("title", ""),
            )
        )
        return {"entries": entries_list}

    @classmethod
    def from_jsonable(cls, data: object) -> "PBCState":
        state = cls()
        if isinstance(data, dict) and "entries" in data:
            entries = data.get("entries")
            if isinstance(entries, list):
                for entry in entries:
                    if not isinstance(entry, dict):
                        continue
                    normalized = {
                        "serial": entry.get("serial")
                        if isinstance(entry.get("serial"), int)
                        else None,
                        "title": entry.get("title", ""),
                        "remark": entry.get("remark", ""),
                    }
                    entry_id = state.ensure_entry(normalized)
                    documents: List[Dict[str, object]] = []
                    for document in entry.get("documents", []):
                        if not isinstance(document, dict):
                            continue
                        documents.append(
                            {
                                "url": document.get("url"),
                                "type": document.get("type"),
                                "title": document.get("title", ""),
                                "downloaded": bool(document.get("downloaded")),
                                "local_path": document.get("local_path"),
                            }
                        )
                    state.merge_documents(entry_id, documents)
            return state
        if isinstance(data, dict):
            converted_items = [
                {"url": url, "name": name}
                for url, name in data.items()
                if isinstance(url, str)
            ]
        elif isinstance(data, list):
            converted_items = []
            for item in data:
                if isinstance(item, str):
                    converted_items.append({"url": item, "name": ""})
                elif isinstance(item, dict):
                    converted_items.append(
                        {"url": item.get("url"), "name": item.get("name", "")}
                    )
        else:
            converted_items = []
        for converted in converted_items:
            url_value = converted.get("url")
            if not isinstance(url_value, str):
                continue
            name = converted.get("name")
            title = str(name) if name is not None else ""
            entry_id = state.ensure_entry({"title": title, "remark": ""})
            document = {
                "url": url_value,
                "type": classify_document_type(url_value),
                "title": title or url_value,
                "downloaded": True,
            }
            state.merge_documents(entry_id, [document])
        return state


def load_state(state_file: Optional[str]) -> PBCState:
    if not state_file or not os.path.exists(state_file):
        return PBCState()
    with open(state_file, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    return PBCState.from_jsonable(data)


def save_state(state_file: Optional[str], state: PBCState) -> None:
    if not state_file:
        return
    os.makedirs(os.path.dirname(state_file), exist_ok=True)
    with open(state_file, "w", encoding="utf-8") as fh:
        json.dump(state.to_jsonable(), fh, ensure_ascii=False, indent=2)


def _local_file_exists(path: Optional[str]) -> bool:
    if not path or not isinstance(path, str):
        return False
    candidate = path if os.path.isabs(path) else os.path.abspath(path)
    return os.path.exists(candidate)


def _ensure_canonical_local_path(
    file_record: Dict[str, object],
    doc_record: Optional[Dict[str, object]],
    url_value: str,
    doc_type: Optional[str],
) -> bool:
    local_path = file_record.get("local_path") if isinstance(file_record, dict) else None
    if not isinstance(local_path, str) or not local_path:
        return False

    expected_name = _structured_filename(url_value, doc_type)
    current_path = Path(local_path)
    expected_path = current_path.with_name(expected_name)

    if current_path.name == expected_name:
        return _local_file_exists(local_path)

    old_abs = current_path if current_path.is_absolute() else (Path.cwd() / current_path)
    new_abs = expected_path if expected_path.is_absolute() else (Path.cwd() / expected_path)

    if old_abs.exists():
        os.makedirs(new_abs.parent, exist_ok=True)
        if old_abs != new_abs and not new_abs.exists():
            old_abs.rename(new_abs)
    elif not new_abs.exists():
        return False

    file_record["local_path"] = str(expected_path)
    if isinstance(doc_record, dict):
        doc_record["local_path"] = str(expected_path)
    return True


def _normalize_output_path(
    value: Optional[str],
    artifact_dir: str,
    subdir: str,
    task_name: Optional[str] = None,
) -> Optional[str]:
    if value is None:
        return None
    if value == "-":
        return "-"
    if os.path.isabs(value):
        return value
    has_separator = os.sep in value or (os.altsep is not None and os.altsep in value)
    parts = [artifact_dir]
    if has_separator:
        parts.append(value)
    else:
        parts.append(subdir)
        if task_name:
            parts.append(task_name)
        parts.append(value)
    return os.path.join(*parts)


def load_config(path: Optional[str]) -> Dict[str, Any]:
    if not path:
        logger.info("No configuration file specified; using defaults")
        return {}
    if not os.path.exists(path):
        logger.info("Configuration file '%s' not found; using defaults", path)
        return {}
    logger.info("Loading configuration from %s", path)
    with open(path, "r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("Configuration file must contain a JSON object")
    return data


def _ensure_unique_path(output_dir: str, filename: str, overwrite: bool = False) -> str:
    base, ext = os.path.splitext(filename)
    candidate = os.path.join(output_dir, filename)
    if overwrite:
        return candidate
    counter = 1
    while os.path.exists(candidate):
        candidate = os.path.join(output_dir, f"{base}_{counter}{ext}")
        counter += 1
    return candidate


def _cache_path_for_url(page_cache_dir: str, url: str) -> str:
    parsed = urlparse(url)
    components = [
        part
        for part in (
            parsed.netloc,
            parsed.path.strip("/") if parsed.path else "",
            parsed.query,
        )
        if part
    ]
    if not components:
        components = [url]
    filename_base = safe_filename("_".join(components))
    if not filename_base:
        filename_base = "page"
    filename = f"{filename_base}.html"
    return os.path.join(page_cache_dir, filename)


EXTENSION_FALLBACK = {
    "pdf": ".pdf",
    "word": ".doc",
    "excel": ".xls",
    "archive": ".zip",
    "text": ".txt",
    "html": ".html",
}


def _structured_filename(file_url: str, doc_type: Optional[str] = None) -> str:
    parsed = urlparse(file_url)
    path = parsed.path or ""
    segments = [segment for segment in path.strip("/").split("/") if segment]

    if segments:
        cleaned_segments: List[str] = []
        for segment in segments:
            seg_stem, seg_ext = os.path.splitext(segment)
            if seg_stem:
                cleaned_segments.append(seg_stem)
            else:
                cleaned_segments.append(segment)
        name_part = "_".join(cleaned_segments)
    else:
        name_part = parsed.netloc or "file"

    if parsed.query:
        query_slug = safe_filename(parsed.query)
        if query_slug:
            name_part = f"{name_part}__{query_slug}" if name_part else query_slug

    sanitized = safe_filename(name_part) or "file"

    basename = os.path.basename(path)
    _, ext = os.path.splitext(basename)
    ext_lower = ext.lower()
    if ext_lower:
        ext_out = ext_lower
    else:
        mapped = EXTENSION_FALLBACK.get((doc_type or "").lower())
        if mapped:
            ext_out = mapped
        else:
            ext_out = ".bin"

    if not ext_out.startswith("."):
        ext_out = f".{ext_out}"

    return f"{sanitized}{ext_out}"


def download_file(
    session: requests.Session,
    file_url: str,
    output_dir: str,
    delay: float,
    jitter: float,
    timeout: float,
    preferred_name: Optional[str] = None,
    overwrite: bool = False,
) -> str:
    _sleep(delay, jitter)
    response = session.get(file_url, stream=True, timeout=timeout)
    response.raise_for_status()
    parsed = urlparse(file_url)
    filename = preferred_name or os.path.basename(parsed.path) or safe_filename(file_url)
    os.makedirs(output_dir, exist_ok=True)
    if overwrite and preferred_name:
        target = os.path.join(output_dir, filename)
    else:
        target = _ensure_unique_path(output_dir, filename)
    with open(target, "wb") as handle:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                handle.write(chunk)
    return target


def download_document(
    session: requests.Session,
    file_url: str,
    output_dir: str,
    delay: float,
    jitter: float,
    timeout: float,
    doc_type: Optional[str],
) -> str:
    normalized_type = (doc_type or "").lower()
    if normalized_type == "html":
        html_content = _fetch(session, file_url, delay, jitter, timeout)
        filename = _structured_filename(file_url, doc_type)
        os.makedirs(output_dir, exist_ok=True)
        target = os.path.join(output_dir, filename)
        with open(target, "w", encoding="utf-8") as handle:
            handle.write(html_content)
        return target
    filename = _structured_filename(file_url, doc_type)
    return download_file(
        session,
        file_url,
        output_dir,
        delay,
        jitter,
        timeout,
        preferred_name=filename,
        overwrite=True,
    )


def collect_new_files(
    session: requests.Session,
    start_url: str,
    output_dir: str,
    state: PBCState,
    delay: float,
    jitter: float,
    timeout: float,
    state_file: Optional[str],
    page_cache_dir: Optional[str],
    allowed_types: Optional[Set[str]] = None,
    verify_local: bool = False,
) -> List[str]:
    downloaded: List[str] = []
    for page_url, soup, _ in iterate_listing_pages(
        session,
        start_url,
        delay,
        jitter,
        timeout,
        page_cache_dir=page_cache_dir,
    ):
        entries = extract_listing_entries(page_url, soup)
        for entry in entries:
            entry_id = state.ensure_entry(entry)
            documents = entry.get("documents")
            if not isinstance(documents, list):
                continue
            for document in documents:
                if isinstance(document, dict) and document.get("type") == "html":
                    state.merge_documents(entry_id, [document])
            for document in documents:
                if not isinstance(document, dict):
                    continue
                file_url = document.get("url")
                doc_type = document.get("type")
                if not isinstance(file_url, str) or not file_url:
                    continue
                normalized_type = (doc_type or classify_document_type(file_url)).lower()
                if allowed_types and normalized_type not in allowed_types:
                    continue
                file_record = state.files.get(file_url, {})
                existing_title = str((file_record or {}).get("title") or "").strip()
                already_downloaded = state.is_downloaded(file_url)
                if already_downloaded and verify_local:
                    if not _local_file_exists(file_record.get("local_path")):
                        state.clear_downloaded(file_url)
                        already_downloaded = False
                        existing_title = ""
                state.merge_documents(entry_id, [document])
                stored_entry = state.entries.get(entry_id, {})
                doc_record = None
                for candidate in stored_entry.get("documents", []):
                    if (
                        isinstance(candidate, dict)
                        and candidate.get("url") == file_url
                    ):
                        doc_record = candidate
                        break
                if not doc_record:
                    continue
                display_name = str(doc_record.get("title") or "").strip()
                if already_downloaded and verify_local:
                    canonical_ok = _ensure_canonical_local_path(
                        file_record,
                        doc_record,
                        file_url,
                        normalized_type,
                    )
                    if not canonical_ok:
                        state.clear_downloaded(file_url)
                        already_downloaded = False
                        existing_title = ""
                if already_downloaded:
                    if display_name and display_name != existing_title:
                        save_state(state_file, state)
                        print(
                            f"Updated name for existing file: {display_name} -> {file_url}"
                        )
                    label = display_name or existing_title or file_url
                    print(f"Skipping existing file: {label} -> {file_url}")
                    continue
                try:
                    path = download_document(
                        session,
                        file_url,
                        output_dir,
                        delay,
                        jitter,
                        timeout,
                        normalized_type,
                    )
                    downloaded.append(path)
                    label = display_name or stored_entry.get("title") or file_url
                    state.mark_downloaded(
                        entry_id,
                        file_url,
                        display_name or label,
                        normalized_type,
                        path,
                    )
                    save_state(state_file, state)
                    print(f"Downloaded: {label} -> {file_url}")
                except Exception as exc:
                    print(f"Failed to download {file_url}: {exc}")
    return downloaded


def download_from_structure(
    structure_path: str,
    output_dir: str,
    state_file: Optional[str],
    delay: float,
    jitter: float,
    timeout: float,
    allowed_types: Optional[Set[str]] = None,
    verify_local: bool = False,
) -> List[str]:
    with open(structure_path, "r", encoding="utf-8") as handle:
        data = json.load(handle)
    entries = data.get("entries")
    if not isinstance(entries, list):
        return []
    session = _create_session()
    state = load_state(state_file)
    downloaded: List[str] = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        entry_id = state.ensure_entry(entry)
        documents = entry.get("documents")
        if not isinstance(documents, list):
            continue
        for document in documents:
            if isinstance(document, dict) and document.get("type") == "html":
                state.merge_documents(entry_id, [document])
        for document in documents:
            if not isinstance(document, dict):
                continue
            file_url = document.get("url")
            doc_type = document.get("type")
            if not isinstance(file_url, str) or not file_url:
                continue
            normalized_type = (doc_type or classify_document_type(file_url)).lower()
            if allowed_types and normalized_type not in allowed_types:
                continue
            file_record = state.files.get(file_url, {})
            existing_title = str((file_record or {}).get("title") or "").strip()
            already_downloaded = state.is_downloaded(file_url)
            if already_downloaded and verify_local:
                if not _local_file_exists(file_record.get("local_path")):
                    state.clear_downloaded(file_url)
                    already_downloaded = False
                    existing_title = ""
            state.merge_documents(entry_id, [document])
            stored_entry = state.entries.get(entry_id, {})
            doc_record = None
            for candidate in stored_entry.get("documents", []):
                if (
                    isinstance(candidate, dict)
                    and candidate.get("url") == file_url
                ):
                    doc_record = candidate
                    break
            if not doc_record:
                continue
            display_name = str(doc_record.get("title") or "").strip()
            if already_downloaded and verify_local:
                canonical_ok = _ensure_canonical_local_path(
                    file_record,
                    doc_record,
                    file_url,
                    normalized_type,
                )
                if not canonical_ok:
                    state.clear_downloaded(file_url)
                    already_downloaded = False
                    existing_title = ""
            if already_downloaded:
                if display_name and display_name != existing_title:
                    save_state(state_file, state)
                    print(f"Updated name for existing file: {display_name} -> {file_url}")
                label = display_name or existing_title or file_url
                print(f"Skipping existing file: {label} -> {file_url}")
                continue
            try:
                path = download_document(
                    session,
                    file_url,
                    output_dir,
                    delay,
                    jitter,
                    timeout,
                    normalized_type,
                )
                downloaded.append(path)
                label = display_name or stored_entry.get("title") or file_url
                state.mark_downloaded(
                    entry_id,
                    file_url,
                    display_name or label,
                    normalized_type,
                    path,
                )
                save_state(state_file, state)
                print(f"Downloaded: {label} -> {file_url}")
            except Exception as exc:
                print(f"Failed to download {file_url}: {exc}")
    save_state(state_file, state)
    return downloaded


def prefetch_listing_pages(
    start_url: str,
    delay: float,
    jitter: float,
    timeout: float,
    page_cache_dir: str,
) -> int:
    logger.info("Prefetching listing pages for %s", start_url)
    os.makedirs(page_cache_dir, exist_ok=True)
    session = _create_session()
    page_count = 0
    for page_url, _, html_path in iterate_listing_pages(
        session,
        start_url,
        delay,
        jitter,
        timeout,
        page_cache_dir=page_cache_dir,
        use_cache=False,
        refresh_cache=True,
    ):
        page_count += 1
        logger.info(
            "Prefetched page %d: %s -> %s",
            page_count,
            page_url,
            html_path or "(none)",
        )
    logger.info(
        "Prefetch completed for %s: %d page(s) cached",
        start_url,
        page_count,
    )
    return page_count


def snapshot_listing(
    start_url: str,
    delay: float,
    jitter: float,
    timeout: float,
    page_cache_dir: Optional[str] = None,
    *,
    use_cache: bool = False,
    refresh_cache: bool = False,
) -> Dict[str, object]:
    logger.info("Starting listing snapshot for %s", start_url)
    session = _create_session()
    state = PBCState()
    pages: List[Dict[str, object]] = []
    if page_cache_dir:
        os.makedirs(page_cache_dir, exist_ok=True)
    page_count = 0
    assigned_serials: Set[str] = {
        entry_id
        for entry_id, entry in state.entries.items()
        if isinstance(entry, dict) and isinstance(entry.get("serial"), int)
    }
    serial_counter = (
        max(
            (
                entry.get("serial")
                for entry in state.entries.values()
                if isinstance(entry, dict) and isinstance(entry.get("serial"), int)
            ),
            default=0,
        )
        if state.entries
        else 0
    )
    for page_url, soup, html_path in iterate_listing_pages(
        session,
        start_url,
        delay,
        jitter,
        timeout,
        page_cache_dir=page_cache_dir,
        use_cache=use_cache,
        refresh_cache=refresh_cache,
    ):
        page_count += 1
        logger.info("Processing listing page %d: %s", page_count, page_url)
        initial_count = len(state.entries)
        entries = extract_listing_entries(page_url, soup)
        pages.append(
            {
                "url": page_url,
                "html_path": html_path,
                "pagination": extract_pagination_meta(page_url, soup, start_url),
            }
        )
        for entry in entries:
            entry_id = state.ensure_entry(entry)
            documents = entry.get("documents")
            if isinstance(documents, list):
                state.merge_documents(entry_id, documents)
            stored_entry = state.entries.get(entry_id, {})
            current_serial = stored_entry.get("serial") if isinstance(stored_entry, dict) else None
            if not isinstance(current_serial, int) or entry_id not in assigned_serials:
                serial_counter += 1
                if isinstance(stored_entry, dict):
                    stored_entry["serial"] = serial_counter
                assigned_serials.add(entry_id)
        unique_added = len(state.entries) - initial_count
        logger.info(
            "Page %d yielded %d entries (%d new, %d total unique)",
            page_count,
            len(entries),
            unique_added if unique_added >= 0 else 0,
            len(state.entries),
        )
    result = state.to_jsonable()
    if pages:
        result["pages"] = pages
    logger.info(
        "Completed listing snapshot for %s: %d page(s), %d unique entries",
        start_url,
        page_count,
        len(state.entries),
    )
    return result


def fetch_listing_html(
    start_url: str,
    delay: float,
    jitter: float,
    timeout: float,
) -> str:
    session = _create_session()
    return _fetch(session, start_url, delay, jitter, timeout)


def snapshot_local_file(path: str, base_url: Optional[str] = None) -> Dict[str, object]:
    snapshot = _parser_snapshot_local_file(path, base_url)
    state = PBCState()
    for entry in snapshot.get("entries", []):
        entry_id = state.ensure_entry(entry)
        documents = entry.get("documents")
        if isinstance(documents, list):
            state.merge_documents(entry_id, documents)
    result = state.to_jsonable()
    result["pages"] = [
        {
            "url": path,
            "html_path": path,
            "pagination": snapshot.get("pagination", {}),
        }
    ]
    result["pagination"] = snapshot.get("pagination", {})
    return result


def monitor_once(
    start_url: str,
    output_dir: str,
    state_file: Optional[str],
    delay: float,
    jitter: float,
    timeout: float,
    page_cache_dir: Optional[str],
    allowed_types: Optional[Set[str]] = None,
    verify_local: bool = False,
) -> List[str]:
    session = _create_session()
    state = load_state(state_file)
    if page_cache_dir:
        os.makedirs(page_cache_dir, exist_ok=True)
    new_files = collect_new_files(
        session,
        start_url,
        output_dir,
        state,
        delay,
        jitter,
        timeout,
        state_file,
        page_cache_dir,
        allowed_types,
        verify_local,
    )
    save_state(state_file, state)
    return new_files


def _compute_sleep_seconds(min_hours: float, max_hours: float) -> float:
    min_seconds = min_hours * 3600
    max_seconds = max_hours * 3600
    if max_seconds < min_seconds:
        raise ValueError("max_hours must be greater than or equal to min_hours")
    return random.uniform(min_seconds, max_seconds)


def monitor_loop(
    start_url: str,
    output_dir: str,
    state_file: Optional[str],
    delay: float,
    jitter: float,
    timeout: float,
    min_hours: float,
    max_hours: float,
    page_cache_dir: Optional[str],
    allowed_types: Optional[Set[str]] = None,
    verify_local: bool = False,
) -> None:
    iteration = 0
    while True:
        iteration += 1
        print(f"[{datetime.now().isoformat(timespec='seconds')}] Iteration {iteration} start")
        new_files = monitor_once(
            start_url,
            output_dir,
            state_file,
            delay,
            jitter,
            timeout,
            page_cache_dir,
            allowed_types,
            verify_local,
        )
        if new_files:
            print(f"New files downloaded: {len(new_files)}")
        else:
            print("No new files found")
        sleep_seconds = _compute_sleep_seconds(min_hours, max_hours)
        print(f"Sleeping for {int(sleep_seconds)} seconds before next check")
        time.sleep(sleep_seconds)


def _resolve_setting(
    cli_value: Optional[Any],
    config: Dict[str, Any],
    key: str,
    fallback: Optional[Any] = None,
) -> Optional[Any]:
    if cli_value is not None:
        return cli_value
    if config and key in config:
        return config[key]
    return fallback


def main(argv: Optional[Sequence[str]] = None) -> None:
    parser = argparse.ArgumentParser(description="Monitor PBC attachment updates")
    parser.add_argument("output_dir", nargs="?", help="directory for downloaded files")
    parser.add_argument("start_url", nargs="?", help="listing URL to monitor")
    parser.add_argument(
        "--config",
        default="pbc_config.json",
        help="path to JSON config with default settings",
    )
    parser.add_argument(
        "--artifact-dir",
        default=None,
        help="base directory for cached pages, snapshots, and state",
    )
    parser.add_argument(
        "--state-file",
        default=None,
        help="path to JSON file tracking downloaded attachment URLs",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=None,
        help="base delay in seconds before each request",
    )
    parser.add_argument(
        "--jitter",
        type=float,
        default=None,
        help="additional random delay in seconds",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=None,
        help="HTTP timeout in seconds",
    )
    parser.add_argument(
        "--min-hours",
        type=float,
        default=None,
        help="minimum hours between checks when running continuously",
    )
    parser.add_argument(
        "--max-hours",
        type=float,
        default=None,
        help="maximum hours between checks when running continuously",
    )
    parser.add_argument(
        "--dump-structure",
        nargs="?",
        const="structure.json",
        help="dump parsed listing structure to stdout or given file",
    )
    parser.add_argument(
        "--download-from-structure",
        nargs="?",
        const="structure.json",
        help="download attachments defined in a structure snapshot",
    )
    parser.add_argument(
        "--dump-from-file",
        metavar="HTML",
        nargs="?",
        const="page.html",
        help="parse local HTML file and dump structure to stdout",
    )
    parser.add_argument(
        "--fetch-page",
        nargs="?",
        const="page.html",
        help="download start page HTML to stdout or given file",
    )
    parser.add_argument(
        "--prefetch-pages",
        action="store_true",
        help="cache all listing pages before parsing or downloading",
    )
    parser.add_argument(
        "--refresh-pages",
        action="store_true",
        help="force re-downloading listing pages even if cached",
    )
    parser.add_argument(
        "--use-cached-pages",
        action="store_true",
        help="reuse cached listing pages when available instead of fetching",
    )
    parser.add_argument(
        "--task",
        default=None,
        help="name of task to run when multiple are configured",
    )
    parser.add_argument(
        "--run-once",
        action="store_true",
        help="perform a single check instead of looping",
    )
    parser.add_argument(
        "--verify-local",
        action="store_true",
        help="re-download attachments if recorded local files are missing",
    )
    args = parser.parse_args(argv)

    if not logging.getLogger().handlers:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
        )

    config = load_config(args.config)
    artifact_dir_value = _resolve_setting(args.artifact_dir, config, "artifact_dir", "artifacts")
    artifact_dir = os.path.abspath(str(artifact_dir_value))
    logger.info("Using artifact directory: %s", artifact_dir)

    tasks = _build_tasks(args, config, artifact_dir)
    if not tasks:
        raise SystemExit("No tasks configured")

    logger.info("Executing %d task(s)", len(tasks))

    for task in tasks:
        _run_task(task, args, config, artifact_dir)


if __name__ == "__main__":
    main()
