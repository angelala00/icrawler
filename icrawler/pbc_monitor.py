from __future__ import annotations

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

DOCUMENT_TYPE_MAP = {
    ".pdf": "pdf",
    ".doc": "word",
    ".docx": "word",
    ".xls": "excel",
    ".xlsx": "excel",
    ".zip": "archive",
    ".rar": "archive",
    ".htm": "html",
    ".html": "html",
    ".txt": "text",
}


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

_GENERIC_PHRASE_PATTERNS = [
    re.compile(
        r"下载\s*(?:word|pdf|docx?|xls|xlsx|zip|rar)\s*(?:版)?",
        re.IGNORECASE,
    ),
    re.compile(
        r"(?:word|pdf|docx?|xls|xlsx|zip|rar)\s*下载",
        re.IGNORECASE,
    ),
    re.compile(r"附件\s*(?:下载|查看)", re.IGNORECASE),
    re.compile(r"点击\s*(?:下载|查看)", re.IGNORECASE),
]


def _ancestor_preceding_text(tag: Tag, max_levels: int = 4) -> List[str]:
    texts: List[str] = []
    current: Optional[Tag] = tag
    depth = 0
    while current is not None and depth < max_levels:
        parent = current.parent
        if not isinstance(parent, Tag):
            break
        pieces: List[str] = []
        for child in parent.children:
            if child is current:
                break
            if isinstance(child, NavigableString):
                text = str(child)
            elif isinstance(child, Tag):
                text = child.get_text(" ", strip=True)
            else:
                continue
            text = re.sub(r"\s+", " ", text or "").strip()
            if text:
                pieces.append(text)
        if pieces:
            texts.append(" ".join(pieces))
        current = parent
        depth += 1
        if parent.name in {"body", "html"}:
            break
    return texts


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
    insertion_index = 1 if has_title else 0
    if preceding_parts:
        candidates.insert(insertion_index, " ".join(preceding_parts))
        insertion_index += 1

    for context_text in _ancestor_preceding_text(tag):
        candidates.insert(insertion_index, context_text)
        insertion_index += 1

    container = tag.find_parent(["li", "p"])
    if container:
        container_text = container.get_text(" ", strip=True)
        container_text = re.sub(r"\s+", " ", container_text)
        if container_text:
            candidates.append(container_text)

    # Remove duplicates while preserving order
    def _tidy(text: str) -> str:
        text = re.sub(r"\s+", " ", text).strip()
        for pattern in _GENERIC_PHRASE_PATTERNS:
            text = pattern.sub(" ", text)
        text = re.sub(r"\s+", " ", text).strip()
        text = re.sub(r"([：:])\s+", r"\1", text)
        for word in GENERIC_LINK_TEXT:
            text = re.sub(rf"{re.escape(word)}$", "", text, flags=re.IGNORECASE).strip()
        text = text.rstrip(":：-—··•·").strip()
        if len(text) > 200:
            text = text[:200].strip()
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


def _legacy_extract_file_links(
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


def _parse_serial(text: str) -> Optional[int]:
    if not text:
        return None
    cleaned = re.sub(r"[\s\u3000]+", "", text)
    cleaned = cleaned.strip("．.、)")
    cleaned = cleaned.strip("(")
    if cleaned.isdigit():
        try:
            return int(cleaned)
        except ValueError:
            return None
    return None


def _extract_remark(cell: Tag, title_text: str) -> str:
    text = cell.get_text(" ", strip=True)
    if not text:
        return ""
    if title_text:
        index = text.find(title_text)
        if index != -1:
            text = (text[:index] + text[index + len(title_text) :]).strip()
    return text.strip()


def _extract_structured_entries(
    page_url: str,
    soup: BeautifulSoup,
    suffixes: Sequence[str],
) -> List[Dict[str, object]]:
    entries: List[Dict[str, object]] = []
    for row in soup.find_all("tr"):
        cells = [
            cell
            for cell in row.find_all(["td", "th"], recursive=False)
            if isinstance(cell, Tag)
        ]
        if len(cells) < 2:
            continue
        serial = _parse_serial(cells[0].get_text(" ", strip=True))
        if serial is None:
            continue
        link_cell = cells[1]
        title_link = link_cell.find("a", href=True)
        if not title_link:
            continue
        raw_href = title_link.get("href", "").strip()
        if not raw_href:
            continue
        detail_url = urljoin(page_url, raw_href)
        link_type = _classify_document_type(detail_url)
        if link_type != "html":
            continue
        title = title_link.get_text(" ", strip=True)
        remark = _extract_remark(link_cell, title)
        extra_notes: List[str] = []
        for extra_cell in cells[2:]:
            cell_text = extra_cell.get_text(" ", strip=True)
            for link in extra_cell.find_all("a", href=True):
                link_text = link.get_text(" ", strip=True)
                if link_text:
                    cell_text = cell_text.replace(link_text, "", 1).strip()
            if cell_text:
                extra_notes.append(cell_text)
        if extra_notes:
            if remark:
                remark = " ".join([remark] + extra_notes).strip()
            else:
                remark = " ".join(extra_notes).strip()

        seen: Set[str] = set()
        documents: List[Dict[str, object]] = []
        documents.append({"type": "html", "url": detail_url, "title": title})
        seen.add(detail_url)

        for link in row.find_all("a", href=True):
            href = link.get("href", "").strip()
            if not href:
                continue
            absolute = urljoin(page_url, href)
            if absolute in seen:
                continue
            doc_type = _classify_document_type(absolute)
            path = urlparse(absolute).path.lower()
            if doc_type == "other" and not any(path.endswith(suffix) for suffix in suffixes):
                continue
            label = _attachment_name(link, absolute)
            if title:
                base_label = label or ""
                if isinstance(serial, int) and base_label.lstrip().startswith(str(serial)):
                    label = title
                elif base_label.count(title) >= 1 and len(base_label) > len(title) + 5:
                    label = title
            if not label and title:
                label = title
            documents.append(
                {"type": doc_type, "url": absolute, "title": label}
            )
            seen.add(absolute)

        if not documents:
            continue
        entries.append(
            {
                "serial": serial,
                "title": title,
                "remark": remark,
                "documents": documents,
            }
        )
    return entries


def extract_listing_entries(
    page_url: str,
    soup: BeautifulSoup,
    suffixes: Sequence[str] = ATTACHMENT_SUFFIXES,
) -> List[Dict[str, object]]:
    structured = _extract_structured_entries(page_url, soup, suffixes)
    if structured:
        return structured
    fallback: List[Dict[str, object]] = []
    for index, (file_url, display_name) in enumerate(
        _legacy_extract_file_links(page_url, soup, suffixes), start=1
    ):
        doc_type = _classify_document_type(file_url)
        fallback.append(
            {
                "serial": index,
                "title": display_name,
                "remark": "",
                "documents": [
                    {
                        "type": doc_type,
                        "url": file_url,
                        "title": display_name,
                    }
                ],
            }
        )
    return fallback


def extract_file_links(
    page_url: str,
    soup: BeautifulSoup,
    suffixes: Sequence[str] = ATTACHMENT_SUFFIXES,
) -> List[Tuple[str, str]]:
    entries = extract_listing_entries(page_url, soup, suffixes=suffixes)
    flattened: List[Tuple[str, str]] = []
    for entry in entries:
        for document in entry.get("documents", []):
            doc_type = document.get("type")
            if doc_type == "html":
                continue
            url_value = document.get("url")
            if not url_value:
                continue
            flattened.append((url_value, document.get("title", "")))
    return flattened


def _same_listing_dir(start_url: str, candidate: str) -> bool:
    start_path = urlparse(start_url).path
    candidate_path = urlparse(candidate).path
    start_dir = os.path.dirname(start_path)
    return candidate_path.startswith(start_dir)


def _classify_document_type(url: str) -> str:
    path = urlparse(url).path.lower()
    _, ext = os.path.splitext(path)
    if ext in DOCUMENT_TYPE_MAP:
        return DOCUMENT_TYPE_MAP[ext]
    if not ext:
        return "html"
    return "other"


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
                doc_type = _classify_document_type(url_value)
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
                "type": _classify_document_type(url_value),
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
    with open(state_file, "w", encoding="utf-8") as fh:
        json.dump(state.to_jsonable(), fh, ensure_ascii=False, indent=2)


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
) -> List[str]:
    downloaded: List[str] = []
    for page_url, soup in iterate_listing_pages(session, start_url, delay, jitter, timeout):
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
                        doc_type or _classify_document_type(file_url),
                        path,
                    )
                    save_state(state_file, state)
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
    state = load_state(state_file)
    new_files = collect_new_files(
        session,
        start_url,
        output_dir,
        state,
        delay,
        jitter,
        timeout,
        state_file,
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
