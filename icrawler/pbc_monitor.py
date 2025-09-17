from __future__ import annotations

import argparse
import json
import os
import random
import time
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from .crawler import safe_filename
from .fetcher import DEFAULT_HEADERS, get as http_get, sleep_with_jitter
from .parser import (
    extract_listing_entries as parser_extract_listing_entries,
    extract_file_links as parser_extract_file_links,
    extract_pagination_links as parser_extract_pagination_links,
    extract_pagination_meta as parser_extract_pagination_meta,
    classify_document_type,
    snapshot_entries as parser_snapshot_entries,
    snapshot_local_file as parser_snapshot_local_file,
)


def extract_listing_entries(
    page_url: str,
    soup: BeautifulSoup,
    suffixes: Optional[Sequence[str]] = None,
) -> List[Dict[str, object]]:
    if suffixes is None:
        return parser_extract_listing_entries(page_url, soup)
    return parser_extract_listing_entries(page_url, soup, suffixes)


def extract_file_links(
    page_url: str,
    soup: BeautifulSoup,
    suffixes: Optional[Sequence[str]] = None,
) -> List[Tuple[str, str]]:
    if suffixes is None:
        return parser_extract_file_links(page_url, soup)
    return parser_extract_file_links(page_url, soup, suffixes)


def extract_pagination_links(
    current_url: str,
    soup: BeautifulSoup,
    start_url: str,
) -> List[str]:
    return parser_extract_pagination_links(current_url, soup, start_url)


def snapshot_entries(html: str, base_url: str) -> Dict[str, object]:
    return parser_snapshot_entries(html, base_url)


def snapshot_local_file(path: str) -> Dict[str, object]:
    return parser_snapshot_local_file(path)


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
) -> Iterable[Tuple[str, BeautifulSoup]]:
    queue: List[str] = [start_url]
    visited: Set[str] = set()
    while queue:
        url = queue.pop(0)
        if url in visited:
            continue
        html = _fetch(session, url, delay, jitter, timeout)
        soup = BeautifulSoup(html, "html.parser")
        yield url, soup
        visited.add(url)
        for link in extract_pagination_links(url, soup, start_url):
            if link not in visited and link not in queue:
                queue.append(link)

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


def load_config(path: Optional[str]) -> Dict[str, Any]:
    if not path:
        return {}
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("Configuration file must contain a JSON object")
    return data


def _ensure_unique_path(output_dir: str, filename: str) -> str:
    base, ext = os.path.splitext(filename)
    candidate = os.path.join(output_dir, filename)
    counter = 1
    while os.path.exists(candidate):
        candidate = os.path.join(output_dir, f"{base}_{counter}{ext}")
        counter += 1
    return candidate


def download_file(
    session: requests.Session,
    file_url: str,
    output_dir: str,
    delay: float,
    jitter: float,
    timeout: float,
) -> str:
    _sleep(delay, jitter)
    response = session.get(file_url, stream=True, timeout=timeout)
    response.raise_for_status()
    parsed = urlparse(file_url)
    filename = os.path.basename(parsed.path) or safe_filename(file_url)
    os.makedirs(output_dir, exist_ok=True)
    target = _ensure_unique_path(output_dir, filename)
    with open(target, "wb") as handle:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                handle.write(chunk)
    return target


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
                if doc_type == "html":
                    continue
                existing_title = ""
                if state.is_downloaded(file_url):
                    existing_title = str(
                        state.files.get(file_url, {}).get("title") or ""
                    ).strip()
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
                if state.is_downloaded(file_url):
                    if display_name and display_name != existing_title:
                        save_state(state_file, state)
                        print(
                            f"Updated name for existing file: {display_name} -> {file_url}"
                        )
                    label = display_name or existing_title or file_url
                    print(f"Skipping existing file: {label} -> {file_url}")
                    continue
                try:
                    path = download_file(
                        session, file_url, output_dir, delay, jitter, timeout
                    )
                    downloaded.append(path)
                    label = display_name or stored_entry.get("title") or file_url
                    state.mark_downloaded(
                        entry_id,
                        file_url,
                        display_name or label,
                        doc_type or classify_document_type(file_url),
                        path,
                    )
                    save_state(state_file, state)
                    print(f"Downloaded: {label} -> {file_url}")
                except Exception as exc:
                    print(f"Failed to download {file_url}: {exc}")
    return downloaded


def snapshot_listing(
    start_url: str,
    delay: float,
    jitter: float,
    timeout: float,
    page_cache_dir: Optional[str] = None,
) -> Dict[str, object]:
    session = requests.Session()
    session.headers.update(DEFAULT_HEADERS)
    state = PBCState()
    pages: List[Dict[str, object]] = []
    if page_cache_dir:
        os.makedirs(page_cache_dir, exist_ok=True)
    for page_url, soup, html_path in iterate_listing_pages(
        session,
        start_url,
        delay,
        jitter,
        timeout,
        page_cache_dir=page_cache_dir,
    ):
        entries = extract_listing_entries(page_url, soup)
        pages.append(
            {
                "url": page_url,
                "html_path": html_path,
                "pagination": parser_extract_pagination_meta(page_url, soup, start_url),
            }
        )
        for entry in entries:
            entry_id = state.ensure_entry(entry)
            documents = entry.get("documents")
            if isinstance(documents, list):
                state.merge_documents(entry_id, documents)
    result = state.to_jsonable()
    if pages:
        result["pages"] = pages
    return result


def fetch_listing_html(
    start_url: str,
    delay: float,
    jitter: float,
    timeout: float,
) -> str:
    session = requests.Session()
    session.headers.update(DEFAULT_HEADERS)
    return _fetch(session, start_url, delay, jitter, timeout)


def snapshot_local_file(path: str, base_url: Optional[str] = None) -> Dict[str, object]:
    snapshot = parser_snapshot_local_file(path, base_url)
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
) -> List[str]:
    session = requests.Session()
    session.headers.update(DEFAULT_HEADERS)
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
        "--run-once",
        action="store_true",
        help="perform a single check instead of looping",
    )
    args = parser.parse_args(argv)

    config = load_config(args.config)

    output_dir = _resolve_setting(args.output_dir, config, "output_dir")
    start_url = _resolve_setting(args.start_url, config, "start_url")
    artifact_dir = _resolve_setting(args.artifact_dir, config, "artifact_dir", "artifacts")
    artifact_dir = os.path.abspath(str(artifact_dir))

    def _normalize_output_path(value: Optional[str], subdir: str) -> Optional[str]:
        if value is None:
            return None
        if value == "-":
            return "-"
        if os.path.isabs(value):
            return value
        return os.path.join(artifact_dir, subdir, value)

    pages_dir = os.path.join(artifact_dir, "pages")

    state_value = _resolve_setting(args.state_file, config, "state_file", "state.json")
    state_file = _normalize_output_path(state_value, "state")
    delay = float(_resolve_setting(args.delay, config, "delay", 3.0))
    jitter = float(_resolve_setting(args.jitter, config, "jitter", 2.0))
    timeout = float(_resolve_setting(args.timeout, config, "timeout", 30.0))
    min_hours = float(_resolve_setting(args.min_hours, config, "min_hours", 20.0))
    max_hours = float(_resolve_setting(args.max_hours, config, "max_hours", 32.0))
    dump_value = _resolve_setting(args.dump_structure, config, "dump_structure")
    dump_target = _normalize_output_path(dump_value, "structure")
    fetch_value = _resolve_setting(args.fetch_page, config, "fetch_page")
    fetch_target = _normalize_output_path(fetch_value, "pages") if fetch_value else None
    dump_from_file_value = args.dump_from_file
    dump_from_file = _normalize_output_path(dump_from_file_value, "pages") if dump_from_file_value else None

    if not dump_from_file and start_url is None:
        raise SystemExit("start_url must be provided via CLI or config")

    if not fetch_target and not dump_target and not dump_from_file and output_dir is None:
        raise SystemExit("output_dir must be provided via CLI or config")

    if dump_from_file:
        snapshot = snapshot_local_file(dump_from_file, start_url)
        print(json.dumps(snapshot, ensure_ascii=False, indent=2))
        return

    if fetch_target:
        html_content = fetch_listing_html(str(start_url), delay, jitter, timeout)
        if fetch_target == "-":
            print(html_content)
        else:
            os.makedirs(os.path.dirname(fetch_target), exist_ok=True)
            with open(str(fetch_target), "w", encoding="utf-8") as handle:
                handle.write(html_content)
        return

    if dump_target:
        snapshot = snapshot_listing(
            str(start_url),
            delay,
            jitter,
            timeout,
            page_cache_dir=pages_dir,
        )
        if dump_target == "-":
            print(json.dumps(snapshot, ensure_ascii=False, indent=2))
        else:
            os.makedirs(os.path.dirname(dump_target), exist_ok=True)
            with open(str(dump_target), "w", encoding="utf-8") as handle:
                json.dump(snapshot, handle, ensure_ascii=False, indent=2)
        return

    if args.run_once:
        monitor_once(
            str(start_url),
            str(output_dir),
            state_file,
            delay,
            jitter,
            timeout,
            pages_dir,
        )
    else:
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
        )


if __name__ == "__main__":
    main()
