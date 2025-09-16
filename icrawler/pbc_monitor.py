import argparse
import json
import os
import random
import re
import time
from datetime import datetime
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup, Tag, NavigableString

from .crawler import safe_filename


DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9",
}

PAGINATION_TEXT = {"下一页", "下页", "上一页", "末页", "尾页", "首页"}
ATTACHMENT_SUFFIXES = (".pdf", ".doc", ".docx", ".xls", ".xlsx", ".zip", ".rar")


def _sleep(delay: float, jitter: float) -> None:
    if delay > 0 or jitter > 0:
        time.sleep(delay + random.uniform(0, jitter))


def _fetch(session: requests.Session, url: str, delay: float, jitter: float, timeout: float) -> str:
    _sleep(delay, jitter)
    response = session.get(url, timeout=timeout)
    response.raise_for_status()
    encoding = (response.encoding or "").lower()
    if not encoding or encoding == "iso-8859-1":
        response.encoding = response.apparent_encoding or "utf-8"
    return response.text


GENERIC_LINK_TEXT = {
    "下载",
    "查看",
    "详情",
    "点击查看",
    "点击下载",
    "附件",
    "word",
    "pdf",
    "doc",
    "docx",
    "xls",
    "xlsx",
    "zip",
    "rar",
}
GENERIC_LINK_TEXT_LOWER = {text.lower() for text in GENERIC_LINK_TEXT}
_GENERIC_CLEAN_RE = re.compile(r"[\s：:（）()【】\[\]<>“”\"'·、，。；,.;!！?？]")
_GENERIC_SUFFIXES = ("版", "本")
_GENERIC_PATTERN = re.compile(
    r"^(点击)?(查看|下载|附件)?(word|pdf|docx?|xls|xlsx)?(下载|查看)?$"
)


def _attachment_name(tag: Tag, file_url: str) -> str:
    candidates: List[str] = []
    link_text = tag.get_text(" ", strip=True)
    if link_text:
        candidates.append(link_text)
    title_attr = tag.get("title")
    has_title = False
    if title_attr:
        candidates.insert(0, title_attr.strip())
        has_title = True

    # Inspect table structure: prefer text from preceding cells in the same row
    cell = tag.find_parent(["td", "th"])
    if cell and cell.parent and cell.parent.name == "tr":
        cells = [c for c in cell.parent.find_all(["td", "th"]) if isinstance(c, Tag)]
        try:
            idx = cells.index(cell)
        except ValueError:
            idx = -1
        if idx > 0:
            for prev in reversed(cells[:idx]):
                text = prev.get_text(" ", strip=True)
                if text:
                    candidates.insert(0, text)
                    break

    # Look for descriptive text directly before the link
    preceding_parts: List[str] = []
    for sibling in tag.previous_siblings:
        text = ""
        if isinstance(sibling, NavigableString):
            text = str(sibling)
        elif isinstance(sibling, Tag):
            text = sibling.get_text(" ", strip=True)
        text = re.sub(r"\s+", " ", text or "").strip()
        if not text:
            continue
        preceding_parts.insert(0, text)
        if len(" ".join(preceding_parts)) >= 120:
            break
    if preceding_parts:
        insertion_index = 1 if has_title else 0
        candidates.insert(insertion_index, " ".join(preceding_parts))

    container = tag.find_parent(["li", "p"])
    if container:
        container_text = container.get_text(" ", strip=True)
        container_text = re.sub(r"\s+", " ", container_text)
        if container_text:
            candidates.append(container_text)

    # Remove duplicates while preserving order
    def _tidy(text: str) -> str:
        text = re.sub(r"\s+", " ", text).strip()
        text = re.sub(r"([：:])\s+", r"\1", text)
        for word in GENERIC_LINK_TEXT:
            text = re.sub(rf"{re.escape(word)}$", "", text).strip()
        text = text.rstrip(":：").strip()
        return text

    def _is_generic(text: str) -> bool:
        lowered = text.lower()
        lowered = _GENERIC_CLEAN_RE.sub("", lowered)
        for suffix in _GENERIC_SUFFIXES:
            if lowered.endswith(suffix):
                lowered = lowered[: -len(suffix)]
        if not lowered:
            return True
        if lowered in GENERIC_LINK_TEXT_LOWER:
            return True
        return bool(_GENERIC_PATTERN.fullmatch(lowered))

    seen: Set[str] = set()
    ordered_candidates = []
    generic_candidates = []
    for candidate in candidates:
        candidate = _tidy(candidate)
        if not candidate or candidate in seen:
            continue
        seen.add(candidate)
        if _is_generic(candidate):
            generic_candidates.append(candidate)
        else:
            ordered_candidates.append(candidate)

    if ordered_candidates:
        return ordered_candidates[0]

    if generic_candidates:
        return generic_candidates[0]

    parsed = urlparse(file_url)
    filename = os.path.basename(parsed.path)
    if filename:
        return filename
    return safe_filename(file_url)


def extract_file_links(
    page_url: str,
    soup: BeautifulSoup,
    suffixes: Sequence[str] = ATTACHMENT_SUFFIXES,
) -> List[Tuple[str, str]]:
    links: List[Tuple[str, str]] = []
    seen: Set[str] = set()
    for tag in soup.find_all("a", href=True):
        href = tag["href"].strip()
        if not href:
            continue
        absolute = urljoin(page_url, href)
        path = urlparse(absolute).path.lower()
        if not any(path.endswith(suffix) for suffix in suffixes):
            continue
        if absolute in seen:
            continue
        seen.add(absolute)
        links.append((absolute, _attachment_name(tag, absolute)))
    return links


def _same_listing_dir(start_url: str, candidate: str) -> bool:
    start_path = urlparse(start_url).path
    candidate_path = urlparse(candidate).path
    start_dir = os.path.dirname(start_path)
    return candidate_path.startswith(start_dir)


_PAGINATION_RE = re.compile(r"index(?:_\d+)?\.(?:s?html)")


def extract_pagination_links(
    current_url: str, soup: BeautifulSoup, start_url: str
) -> List[str]:
    links: List[str] = []
    seen: Set[str] = set()
    for tag in soup.find_all("a", href=True):
        text = (tag.get_text() or "").strip()
        href = tag["href"].strip()
        if not href:
            continue
        resolved = urljoin(current_url, href)
        if resolved in seen:
            continue
        parsed = urlparse(resolved)
        start_parsed = urlparse(start_url)
        if parsed.netloc and parsed.netloc != start_parsed.netloc:
            continue
        if not _same_listing_dir(start_url, resolved):
            continue
        if text in PAGINATION_TEXT or _PAGINATION_RE.search(parsed.path.lower()):
            seen.add(resolved)
            links.append(resolved)
    return links


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


StateMap = Dict[str, str]


def load_state(state_file: Optional[str]) -> StateMap:
    if not state_file or not os.path.exists(state_file):
        return {}
    with open(state_file, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    state: StateMap = {}
    if isinstance(data, dict):
        for url, name in data.items():
            if isinstance(url, str):
                state[url] = str(name) if name is not None else ""
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, str):
                state[item] = ""
            elif isinstance(item, dict):
                url = item.get("url")
                name = item.get("name", "")
                if isinstance(url, str):
                    state[url] = str(name) if name is not None else ""
    return state


def save_state(state_file: Optional[str], entries: StateMap) -> None:
    if not state_file:
        return
    with open(state_file, "w", encoding="utf-8") as fh:
        serializable = [
            {"url": url, "name": name}
            for url, name in sorted(entries.items(), key=lambda item: item[0])
        ]
        json.dump(serializable, fh, ensure_ascii=False, indent=2)


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
    known_entries: StateMap,
    delay: float,
    jitter: float,
    timeout: float,
    state_file: Optional[str],
) -> List[str]:
    downloaded: List[str] = []
    for page_url, soup in iterate_listing_pages(session, start_url, delay, jitter, timeout):
        for file_url, display_name in extract_file_links(page_url, soup):
            display_name = (display_name or "").strip()
            if file_url in known_entries:
                stored_name = known_entries.get(file_url, "").strip()
                if display_name and display_name != stored_name:
                    known_entries[file_url] = display_name
                    save_state(state_file, known_entries)
                    print(
                        f"Updated name for existing file: {display_name} -> {file_url}"
                    )
                label = display_name or stored_name or file_url
                print(f"Skipping existing file: {label} -> {file_url}")
                continue
            try:
                path = download_file(session, file_url, output_dir, delay, jitter, timeout)
                known_entries[file_url] = display_name
                downloaded.append(path)
                save_state(state_file, known_entries)
                label = display_name or file_url
                print(f"Downloaded: {label} -> {file_url}")
            except Exception as exc:
                print(f"Failed to download {file_url}: {exc}")
    return downloaded


def monitor_once(
    start_url: str,
    output_dir: str,
    state_file: Optional[str],
    delay: float,
    jitter: float,
    timeout: float,
) -> List[str]:
    session = requests.Session()
    session.headers.update(DEFAULT_HEADERS)
    known = load_state(state_file)
    new_files = collect_new_files(
        session,
        start_url,
        output_dir,
        known,
        delay,
        jitter,
        timeout,
        state_file,
    )
    save_state(state_file, known)
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
) -> None:
    iteration = 0
    while True:
        iteration += 1
        print(f"[{datetime.now().isoformat(timespec='seconds')}] Iteration {iteration} start")
        new_files = monitor_once(start_url, output_dir, state_file, delay, jitter, timeout)
        if new_files:
            print(f"New files downloaded: {len(new_files)}")
        else:
            print("No new files found")
        sleep_seconds = _compute_sleep_seconds(min_hours, max_hours)
        print(f"Sleeping for {int(sleep_seconds)} seconds before next check")
        time.sleep(sleep_seconds)


def main(argv: Optional[Sequence[str]] = None) -> None:
    parser = argparse.ArgumentParser(description="Monitor PBC attachment updates")
    parser.add_argument("output_dir", help="directory for downloaded files")
    parser.add_argument("start_url", help="listing URL to monitor")
    parser.add_argument(
        "--state-file",
        default="state.json",
        help="path to JSON file tracking downloaded attachment URLs",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=3.0,
        help="base delay in seconds before each request",
    )
    parser.add_argument(
        "--jitter",
        type=float,
        default=2.0,
        help="additional random delay in seconds",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=30.0,
        help="HTTP timeout in seconds",
    )
    parser.add_argument(
        "--min-hours",
        type=float,
        default=20.0,
        help="minimum hours between checks when running continuously",
    )
    parser.add_argument(
        "--max-hours",
        type=float,
        default=32.0,
        help="maximum hours between checks when running continuously",
    )
    parser.add_argument(
        "--run-once",
        action="store_true",
        help="perform a single check instead of looping",
    )
    args = parser.parse_args(argv)

    if args.run_once:
        monitor_once(args.start_url, args.output_dir, args.state_file, args.delay, args.jitter, args.timeout)
    else:
        monitor_loop(
            args.start_url,
            args.output_dir,
            args.state_file,
            args.delay,
            args.jitter,
            args.timeout,
            args.min_hours,
            args.max_hours,
        )


if __name__ == "__main__":
    main()
