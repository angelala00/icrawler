"""Utilities for extracting text content from policy documents.

This module reads entries from a state JSON structure and produces plain
text files for each entry by preferring Word documents, then PDFs, and
finally HTML pages. The extraction results (including any warnings about
image-based PDFs that require OCR) are recorded so the caller can update
the state metadata and create human-readable reports.

The helpers are intentionally independent from the crawler so they can be
used by standalone scripts or tests without invoking the full monitoring
stack.
"""

from __future__ import annotations

import io
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from zipfile import ZipFile

import xml.etree.ElementTree as ET

from bs4 import BeautifulSoup

try:  # Optional dependency used for PDF extraction.
    from pdfminer.high_level import extract_text as _default_pdf_extractor
except Exception:  # pragma: no cover - pdfminer is optional at runtime.
    _default_pdf_extractor = None

from .crawler import safe_filename


# The active PDF text extractor can be swapped in tests.
_pdf_text_extractor = _default_pdf_extractor


def set_pdf_text_extractor(extractor):  # pragma: no cover - exercised in tests
    """Override the PDF text extractor used by :func:`extract_entry_text`."""

    global _pdf_text_extractor
    _pdf_text_extractor = extractor


def reset_pdf_text_extractor():  # pragma: no cover - exercised in tests
    """Restore the default PDF text extractor."""

    global _pdf_text_extractor
    _pdf_text_extractor = _default_pdf_extractor


_DOCUMENT_PRIORITIES = {
    "docx": 3,
    "doc": 3,
    "word": 3,
    "pdf": 2,
    "html": 1,
    "text": 0,
}


def _decode_bytes(data: bytes) -> str:
    """Best-effort decoding for text payloads with common encodings."""

    for encoding in ("utf-8", "utf-16", "utf-16le", "utf-16be", "gb18030", "gbk"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="ignore")


def _extract_docx_text(data: bytes) -> Tuple[Optional[str], Optional[str]]:
    """Extract plain text content from a docx payload."""

    buffer = io.BytesIO(data)
    try:
        with ZipFile(buffer) as archive:
            xml_data = archive.read("word/document.xml")
    except KeyError:
        return None, "docx_document_missing"
    except Exception:
        return None, "docx_read_error"

    try:
        root = ET.fromstring(xml_data)
    except ET.ParseError:
        return None, "docx_parse_error"

    namespace = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    paragraphs: List[str] = []
    for paragraph in root.findall(".//w:p", namespace):
        runs: List[str] = []
        for node in paragraph.findall(".//w:t", namespace):
            if node.text:
                runs.append(node.text)
        if runs:
            paragraphs.append("".join(runs))
    text = "\n".join(paragraphs).strip()
    if not text:
        return None, "docx_empty"
    return text, None


def _normalize_type(declared: Optional[str], suffix: str) -> Optional[str]:
    value = (declared or "").lower().strip() or None
    extension = suffix.lower()
    if extension == ".pdf":
        return "pdf"
    if extension == ".docx":
        return "docx"
    if extension == ".doc":
        return "doc"
    if extension in {".htm", ".html"}:
        return "html"
    if extension in {".txt", ".text", ".md"}:
        return "text"
    if value in {"doc", "docx", "word"}:
        return "docx" if value == "docx" else "doc"
    if value in {"pdf", "html", "text"}:
        return value
    return value


def _resolve_candidate_path(path_value: str, state_dir: Path) -> Optional[Path]:
    if not path_value:
        return None

    candidate = Path(path_value).expanduser()
    search_paths: List[Path] = []
    if candidate.is_absolute():
        search_paths.append(candidate)
    else:
        search_paths.append(state_dir / candidate)
        search_paths.append(state_dir / candidate.name)
        search_paths.append((state_dir / "downloads" / candidate.name))
        parent = state_dir.parent
        search_paths.append(parent / candidate)
        search_paths.append(parent / "downloads" / candidate.name)
        search_paths.append(parent / "downloads" / candidate)

    # Always include the literal candidate for callers that already resolve it.
    search_paths.append(candidate)

    seen: List[Path] = []
    for path in search_paths:
        try:
            resolved = path.resolve()
        except OSError:
            resolved = path
        if resolved in seen:
            continue
        seen.append(resolved)
        if resolved.is_file():
            return resolved
    return None


@dataclass
class DocumentCandidate:
    document: Dict[str, Any]
    path: Path
    declared_type: Optional[str]
    normalized_type: Optional[str]
    priority: int
    order: int


@dataclass
class ExtractionAttempt:
    candidate: DocumentCandidate
    text: Optional[str]
    error: Optional[str]
    needs_ocr: bool
    used: bool = False

    @property
    def normalized_type(self) -> Optional[str]:
        return self.candidate.normalized_type

    @property
    def path(self) -> Path:
        return self.candidate.path


@dataclass
class EntryExtraction:
    entry: Dict[str, Any]
    attempts: List[ExtractionAttempt]
    selected: Optional[ExtractionAttempt]
    text: str
    status: str
    pdf_needs_ocr: bool


def _build_candidates(entry: Dict[str, Any], state_dir: Path) -> List[DocumentCandidate]:
    documents = entry.get("documents") or []
    if not isinstance(documents, list):
        return []

    candidates: List[DocumentCandidate] = []
    for index, document in enumerate(documents):
        if not isinstance(document, dict):
            continue
        path_value = (
            document.get("local_path")
            or document.get("localPath")
            or document.get("path")
        )
        if not isinstance(path_value, str) or not path_value:
            continue
        resolved = _resolve_candidate_path(path_value, state_dir)
        if not resolved:
            continue
        declared_type = document.get("type")
        normalized = _normalize_type(declared_type if isinstance(declared_type, str) else None, resolved.suffix)
        priority = _DOCUMENT_PRIORITIES.get(normalized or "", -1)
        candidates.append(
            DocumentCandidate(
                document=document,
                path=resolved,
                declared_type=declared_type if isinstance(declared_type, str) else None,
                normalized_type=normalized,
                priority=priority,
                order=index,
            )
        )
    candidates.sort(key=lambda item: (-item.priority, item.order))
    return candidates


def _attempt_extract(candidate: DocumentCandidate) -> ExtractionAttempt:
    path = candidate.path
    normalized = candidate.normalized_type or (path.suffix.lower().lstrip(".") or None)

    try:
        data = path.read_bytes()
    except FileNotFoundError:
        return ExtractionAttempt(candidate, text=None, error="file_missing", needs_ocr=False)

    if normalized not in {"docx"}:
        if data[:2] == b"PK":
            buffer = io.BytesIO(data)
            try:
                with ZipFile(buffer) as archive:
                    if "word/document.xml" in archive.namelist():
                        normalized = "docx"
                        candidate.normalized_type = "docx"
            except Exception:
                pass

    if normalized in {"docx"}:
        text, error = _extract_docx_text(data)
        return ExtractionAttempt(candidate, text=text, error=error, needs_ocr=False)
    if normalized in {"doc", "word"}:
        text = _decode_bytes(data)
        stripped = text.strip()
        if not stripped:
            return ExtractionAttempt(candidate, text=None, error="doc_empty", needs_ocr=False)
        return ExtractionAttempt(candidate, text=text, error=None, needs_ocr=False)
    if normalized == "html":
        decoded = _decode_bytes(data)
        soup = BeautifulSoup(decoded, "html.parser")
        for tag in soup(["script", "style"]):
            tag.decompose()
        text = soup.get_text("\n", strip=True)
        if not text.strip():
            return ExtractionAttempt(candidate, text=None, error="html_empty", needs_ocr=False)
        return ExtractionAttempt(candidate, text=text, error=None, needs_ocr=False)
    if normalized == "pdf":
        if _pdf_text_extractor is None:
            return ExtractionAttempt(candidate, text=None, error="pdf_support_unavailable", needs_ocr=False)
        try:
            text = _pdf_text_extractor(str(path))
        except Exception:
            return ExtractionAttempt(candidate, text=None, error="pdf_parse_error", needs_ocr=False)
        stripped = (text or "").strip()
        needs_ocr = not bool(stripped)
        if not stripped:
            return ExtractionAttempt(candidate, text=text or "", error=None, needs_ocr=needs_ocr)
        return ExtractionAttempt(candidate, text=text, error=None, needs_ocr=needs_ocr)

    # Fallback: treat as plain text.
    text = _decode_bytes(data)
    stripped = text.strip()
    if not stripped:
        return ExtractionAttempt(candidate, text=None, error="text_empty", needs_ocr=False)
    return ExtractionAttempt(candidate, text=text, error=None, needs_ocr=False)


def extract_entry(entry: Dict[str, Any], state_dir: Path) -> EntryExtraction:
    candidates = _build_candidates(entry, state_dir)
    attempts: List[ExtractionAttempt] = []
    pdf_needs_ocr = False
    selected: Optional[ExtractionAttempt] = None
    fallback: Optional[ExtractionAttempt] = None

    for candidate in candidates:
        attempt = _attempt_extract(candidate)
        attempts.append(attempt)
        if attempt.normalized_type == "pdf" and attempt.needs_ocr:
            pdf_needs_ocr = True
        text_value = (attempt.text or "").strip()
        if text_value:
            attempt.used = True
            selected = attempt
            break
        if fallback is None:
            fallback = attempt

    if not candidates:
        return EntryExtraction(entry, attempts=[], selected=None, text="", status="no_source", pdf_needs_ocr=False)

    if selected is None and fallback is not None:
        fallback.used = True
        selected = fallback

    if selected is None and attempts:
        attempts[0].used = True
        selected = attempts[0]

    text_result = selected.text if selected and selected.text is not None else ""
    stripped = text_result.strip()

    if selected is None:
        status = "no_source"
    elif selected.error:
        status = "error"
    elif stripped:
        status = "success"
    elif selected.needs_ocr and (selected.normalized_type == "pdf" or pdf_needs_ocr):
        status = "needs_ocr"
    else:
        status = "empty"

    return EntryExtraction(entry, attempts=attempts, selected=selected, text=text_result, status=status, pdf_needs_ocr=pdf_needs_ocr)


@dataclass
class EntryTextRecord:
    entry_index: int
    serial: Optional[int]
    title: str
    text_path: Path
    status: str
    source_type: Optional[str]
    source_path: Optional[str]
    pdf_needs_ocr: bool
    attempts: List[ExtractionAttempt] = field(default_factory=list)


@dataclass
class ProcessReport:
    records: List[EntryTextRecord]

    @property
    def pdf_needs_ocr(self) -> List[EntryTextRecord]:
        return [record for record in self.records if record.pdf_needs_ocr]


def _build_filename(entry: Dict[str, Any], attempt: Optional[ExtractionAttempt], index: int, used: Dict[str, int]) -> str:
    parts: List[str] = []
    serial = entry.get("serial")
    if isinstance(serial, int):
        parts.append(f"{serial:04d}")
    title = entry.get("title")
    if isinstance(title, str) and title.strip():
        parts.append(safe_filename(title))
    remark = entry.get("remark")
    if not parts and isinstance(remark, str) and remark.strip():
        parts.append(safe_filename(remark))
    if not parts:
        parts.append(f"entry_{index + 1:04d}")
    if attempt and attempt.normalized_type:
        parts.append(attempt.normalized_type)
    base = "_".join(filter(None, parts))
    counter = used.get(base, 0)
    used[base] = counter + 1
    if counter:
        base = f"{base}_{counter}"
    return f"{base}.txt"


def _summarize_attempt(attempt: ExtractionAttempt) -> Dict[str, Any]:
    summary: Dict[str, Any] = {
        "type": attempt.normalized_type or attempt.candidate.declared_type,
        "path": str(attempt.path),
        "used": attempt.used,
        "needs_ocr": attempt.needs_ocr,
    }
    if attempt.error:
        summary["error"] = attempt.error
    if attempt.text is not None:
        summary["char_count"] = len(attempt.text)
    return summary


def _build_text_content(text: str) -> str:
    """Return the plain extracted text content for persistence."""

    if not text:
        return ""
    return text


def process_state_data(
    state_data: Dict[str, Any],
    output_dir: Path,
    *,
    state_path: Optional[Path] = None,
) -> ProcessReport:
    """Extract text for every entry and update *state_data* in place."""

    output_dir.mkdir(parents=True, exist_ok=True)
    state_dir = state_path.parent if state_path else output_dir
    used_names: Dict[str, int] = {}
    records: List[EntryTextRecord] = []
    entries = state_data.get("entries")
    if not isinstance(entries, list):
        return ProcessReport(records=[])

    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            continue
        extraction = extract_entry(entry, state_dir)
        filename = _build_filename(entry, extraction.selected, index, used_names)
        text_path = output_dir / filename
        text_content = extraction.text if extraction.text is not None else ""
        text_output = _build_text_content(text_content)
        text_path.write_text(text_output, encoding="utf-8")

        document_url = f"local-text://{filename}"
        text_document: Dict[str, Any] = {
            "url": document_url,
            "type": "text",
            "title": f"{entry.get('title', '')}（文本）".strip() or "文本提取",
            "downloaded": True,
            "local_path": str(text_path),
            "extraction_status": extraction.status,
        }
        if extraction.selected:
            candidate = extraction.selected.candidate
            source_type = extraction.selected.normalized_type or candidate.declared_type
            text_document["source_type"] = source_type
            text_document["source_local_path"] = str(candidate.path)
            if candidate.document.get("url"):
                text_document["source_url"] = candidate.document.get("url")
        if extraction.pdf_needs_ocr:
            text_document["needs_ocr"] = True
        if extraction.attempts:
            text_document["extraction_attempts"] = [_summarize_attempt(attempt) for attempt in extraction.attempts]

        documents = entry.setdefault("documents", [])
        if isinstance(documents, list):
            existing = None
            for document in documents:
                if not isinstance(document, dict):
                    continue
                if document.get("url") == document_url:
                    existing = document
                    break
            if existing is None:
                documents.append(text_document)
            else:
                existing.update(text_document)

        record = EntryTextRecord(
            entry_index=index,
            serial=entry.get("serial") if isinstance(entry.get("serial"), int) else None,
            title=entry.get("title") or "",
            text_path=text_path,
            status=extraction.status,
            source_type=(
                extraction.selected.normalized_type if extraction.selected and extraction.selected.normalized_type
                else extraction.selected.candidate.declared_type if extraction.selected else None
            ),
            source_path=str(extraction.selected.candidate.path) if extraction.selected else None,
            pdf_needs_ocr=extraction.pdf_needs_ocr,
            attempts=extraction.attempts,
        )
        records.append(record)

    return ProcessReport(records=records)

