import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from searcher.policy_finder import (  # noqa: E402
    Entry,
    extract_clause_from_entry,
    parse_clause_reference,
)


def test_extract_clause_handles_bullet_articles(tmp_path):
    doc_path = tmp_path / "bullet.txt"
    doc_path.write_text(
        "前言\n"
        "一、第一部分要求\n"
        "具体内容A\n"
        "二、第二部分要求\n"
        "具体内容B\n",
        "utf-8",
    )
    entry = Entry(
        id=1,
        title="测试文件",
        remark="",
        documents=[{"type": "text", "local_path": str(doc_path)}],
    )
    entry.build()

    reference_one = parse_clause_reference("第一条")
    assert reference_one is not None
    result_one = extract_clause_from_entry(entry, reference_one)
    assert result_one.article_matched is True
    assert result_one.error is None
    assert "第一部分" in (result_one.article_text or "")

    reference_two = parse_clause_reference("第二条")
    assert reference_two is not None
    result_two = extract_clause_from_entry(entry, reference_two)
    assert result_two.article_matched is True
    assert result_two.error is None
    assert "第二部分" in (result_two.article_text or "")
    assert "第一部分" not in (result_two.article_text or "")
