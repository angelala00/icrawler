import json
from pathlib import Path

import pytest

from icrawler import text_pipeline
from icrawler.text_pipeline import process_state_data


def _write_docx(path: Path, text: str) -> None:
    xml = f"""<?xml version='1.0' encoding='UTF-8' standalone='yes'?>
<w:document xmlns:w='http://schemas.openxmlformats.org/wordprocessingml/2006/main'>
  <w:body>
    <w:p><w:r><w:t>{text}</w:t></w:r></w:p>
  </w:body>
</w:document>
"""
    from zipfile import ZipFile

    with ZipFile(path, "w") as archive:
        archive.writestr("word/document.xml", xml)


@pytest.fixture
def fake_pdf_extractor(monkeypatch):
    def extractor(path: str) -> str:
        if path.endswith("with_text.pdf"):
            return "PDF 正文内容"
        if path.endswith("needs_ocr.pdf"):
            return ""
        raise AssertionError(f"unexpected pdf path: {path}")

    monkeypatch.setattr(text_pipeline, "_pdf_text_extractor", extractor)
    return extractor


def test_extract_entry_supports_wps_docx(tmp_path):
    downloads = tmp_path / "downloads"
    downloads.mkdir()

    wps_path = downloads / "policy.wps"
    _write_docx(wps_path, "WPS 文本内容")

    entry = {
        "documents": [
            {
                "url": "http://example.com/policy.wps",
                "type": "doc",
                "local_path": str(wps_path),
            }
        ]
    }

    extraction = text_pipeline.extract_entry(entry, downloads)

    assert extraction.selected is not None
    assert extraction.selected.normalized_type == "docx"
    assert extraction.text == "WPS 文本内容"


def test_process_state_data_extracts_text(tmp_path, fake_pdf_extractor):
    downloads = tmp_path / "downloads"
    downloads.mkdir()

    docx_path = downloads / "policy.docx"
    _write_docx(docx_path, "Word 文本内容")

    pdf_path = downloads / "policy_with_text.pdf"
    pdf_path.write_bytes(b"%PDF-1.4")

    pdf_empty_path = downloads / "policy_needs_ocr.pdf"
    pdf_empty_path.write_bytes(b"%PDF-1.4")

    html_path = downloads / "fallback.html"
    html_path.write_text("<html><body><p>HTML 正文</p></body></html>", encoding="utf-8")

    state_data = {
        "entries": [
            {
                "serial": 1,
                "title": "制度一",
                "remark": "",
                "documents": [
                    {
                        "url": "http://example.com/doc.docx",
                        "type": "doc",
                        "local_path": str(docx_path),
                    }
                ],
            },
            {
                "serial": 2,
                "title": "制度二",
                "documents": [
                    {
                        "url": "http://example.com/policy.pdf",
                        "type": "pdf",
                        "local_path": str(pdf_path),
                    }
                ],
            },
            {
                "serial": 3,
                "title": "制度三",
                "documents": [
                    {
                        "url": "http://example.com/scan.pdf",
                        "type": "pdf",
                        "local_path": str(pdf_empty_path),
                    },
                    {
                        "url": "http://example.com/scan.html",
                        "type": "html",
                        "local_path": str(html_path),
                    },
                ],
            },
            {
                "serial": 4,
                "title": "制度四",
                "documents": [],
            },
        ]
    }

    state_path = downloads / "policy_state.json"
    state_path.write_text(json.dumps(state_data, ensure_ascii=False), encoding="utf-8")

    output_dir = tmp_path / "texts"
    report = process_state_data(state_data, output_dir, state_path=state_path)

    assert len(report.records) == 4
    assert len(list(output_dir.iterdir())) == 4

    records_by_serial = {record.serial: record for record in report.records}

    record_one = records_by_serial[1]
    assert record_one.source_type == "docx"
    content_one = record_one.text_path.read_text(encoding="utf-8")
    assert content_one == "Word 文本内容"

    entry_one_docs = [doc for doc in state_data["entries"][0]["documents"] if doc.get("type") == "text"]
    assert len(entry_one_docs) == 1
    assert entry_one_docs[0]["source_type"] == "docx"

    record_two = records_by_serial[2]
    assert record_two.source_type == "pdf"
    assert record_two.status == "success"
    assert not record_two.pdf_needs_ocr
    content_two = record_two.text_path.read_text(encoding="utf-8")
    assert content_two == "PDF 正文内容"

    entry_two_text_doc = [doc for doc in state_data["entries"][1]["documents"] if doc.get("type") == "text"]
    assert entry_two_text_doc[0].get("needs_ocr") is None
    assert entry_two_text_doc[0]["extraction_status"] == "success"

    record_three = records_by_serial[3]
    assert record_three.source_type == "html"
    assert record_three.status == "success"
    assert record_three.pdf_needs_ocr
    content_three = record_three.text_path.read_text(encoding="utf-8")
    assert content_three == "HTML 正文"

    entry_three_text_doc = [doc for doc in state_data["entries"][2]["documents"] if doc.get("type") == "text"]
    assert entry_three_text_doc[0]["needs_ocr"] is True
    attempts = entry_three_text_doc[0]["extraction_attempts"]
    assert attempts[0]["type"] == "pdf"
    assert attempts[0]["needs_ocr"] is True
    assert attempts[0]["used"] is False
    assert attempts[1]["type"] == "html"
    assert attempts[1]["used"] is True

    record_four = records_by_serial[4]
    assert record_four.source_type is None
    assert record_four.status == "no_source"
    content_four = record_four.text_path.read_text(encoding="utf-8")
    assert content_four == ""

    entry_four_docs = [doc for doc in state_data["entries"][3]["documents"] if doc.get("type") == "text"]
    assert entry_four_docs[0]["extraction_status"] == "no_source"

