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
        if path.endswith("layout.pdf"):
            return (
                "Page Header\n\n"
                "Paragraph line one\n"
                "line two\n\n"
                "Page Footer\n"
                "- 1 -\n"
                "\fPage Header\n\n"
                "第二段第一行\n"
                "继续内容\n\n"
                "Page Footer\n"
            )
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


def test_extract_entry_flags_binary_wps(tmp_path):
    downloads = tmp_path / "downloads"
    downloads.mkdir()

    wps_path = downloads / "policy_binary.wps"
    wps_path.write_bytes(b"\xd0\xcf\x11\xe0" + b"\x00" * 128)

    entry = {
        "documents": [
            {
                "url": "http://example.com/policy_binary.wps",
                "type": "doc",
                "local_path": str(wps_path),
            }
        ]
    }

    extraction = text_pipeline.extract_entry(entry, downloads)

    assert extraction.selected is not None
    assert extraction.selected.error == "doc_binary_unsupported"
    assert extraction.status == "error"


def test_extract_entry_normalizes_pdf_text(tmp_path, fake_pdf_extractor):
    downloads = tmp_path / "downloads"
    downloads.mkdir()

    pdf_path = downloads / "layout.pdf"
    pdf_path.write_bytes(b"%PDF-1.4")

    entry = {
        "documents": [
            {
                "url": "http://example.com/layout.pdf",
                "type": "pdf",
                "local_path": str(pdf_path),
            }
        ]
    }

    extraction = text_pipeline.extract_entry(entry, downloads)

    assert extraction.selected is not None
    assert extraction.selected.normalized_type == "pdf"
    assert extraction.text == "Paragraph line one line two\n第二段第一行继续内容"


def test_extract_entry_normalizes_html_text(tmp_path):
    downloads = tmp_path / "downloads"
    downloads.mkdir()

    html_path = downloads / "policy.html"
    html_path.write_text(
        """
<html>
  <body>
    <div>中国人民银行规章</div>
    <div>所在位置 ：</div>
    <div>政府信息公开</div>
    <div>政　　策</div>
    <div>行政规范性文件</div>
    <div>下载word版</div>
    <div>下载pdf版</div>
    <h1>制度标题</h1>
    <p>第一段内容。</p>
    <p>法律声明</p>
    <p>中国人民银行发布</p>
  </body>
</html>
""",
        encoding="utf-8",
    )

    entry = {
        "documents": [
            {
                "url": "http://example.com/policy.html",
                "type": "html",
                "local_path": str(html_path),
            }
        ]
    }

    extraction = text_pipeline.extract_entry(entry, downloads)

    assert extraction.selected is not None
    text = extraction.text
    assert text.splitlines()[0] == "制度标题"
    assert "下载word版" not in text
    assert "中国人民银行规章" not in text
    assert "所在位置" not in text
    assert "法律声明" not in text
    assert not text.endswith("中国人民银行发布")


def test_extract_entry_separates_conclusion_from_article(tmp_path):
    downloads = tmp_path / "downloads"
    downloads.mkdir()

    html_path = downloads / "conclusion.html"
    html_path.write_text(
        """
<html>
  <body>
    <p>八、外国银行境内分行参照本通知执行。</p>
    <p>本通知自2023年12月20日起实施。</p>
  </body>
</html>
""",
        encoding="utf-8",
    )

    entry = {
        "documents": [
            {
                "url": "http://example.com/conclusion.html",
                "type": "html",
                "local_path": str(html_path),
            }
        ]
    }

    extraction = text_pipeline.extract_entry(entry, downloads)

    assert extraction.selected is not None
    lines = extraction.text.splitlines()
    assert lines[0] == "八、外国银行境内分行参照本通知执行。"
    assert lines[1] == ""
    assert lines[2] == "本通知自2023年12月20日起实施。"


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
