import builtins
import importlib
import json
import os
import sys
import tempfile
import types

sys.modules.pop("bs4", None)
importlib.import_module("bs4")

from bs4 import BeautifulSoup

pdfkit_stub = types.SimpleNamespace(from_url=lambda *a, **k: None)
sys.modules.setdefault("pdfkit", pdfkit_stub)

from icrawler import pbc_monitor


def _make_soup(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "html.parser")


def test_extract_file_links():
    html = """
    <html><body>
      <li>通知1：<a href="doc/notice1.PDF">下载</a></li>
      <div class="entry"><span>报告全文</span><a href="/files/report.docx">附件</a></div>
      <a href="index_2.html">下一页</a>
    </body></html>
    """
    soup = _make_soup(html)
    links = pbc_monitor.extract_file_links("http://example.com/list/index.html", soup)
    assert links == [
        (
            "http://example.com/list/doc/notice1.PDF",
            "通知1",
        ),
        (
            "http://example.com/files/report.docx",
            "报告全文",
        ),
    ]


def test_extract_file_links_table_context():
    html = """
    <table>
      <tr>
        <td>中国人民银行公告〔2024〕第1号</td>
        <td><a href="/files/pbc1.doc">word</a> <a href="/files/pbc1.pdf">pdf</a></td>
      </tr>
    </table>
    """
    soup = _make_soup(html)
    links = pbc_monitor.extract_file_links("http://example.com/list/index.html", soup)
    assert links == [
        (
            "http://example.com/files/pbc1.doc",
            "中国人民银行公告〔2024〕第1号",
        ),
        (
            "http://example.com/files/pbc1.pdf",
            "中国人民银行公告〔2024〕第1号",
        )
    ]


def test_extract_file_links_multi_entry_container():
    html = """
    <div class="list">
      <p>标题甲 <a href="/files/a.pdf">下载</a></p>
      <p>标题乙 <a href="/files/b.pdf">下载</a></p>
    </div>
    """
    soup = _make_soup(html)
    links = pbc_monitor.extract_file_links("http://example.com/list/index.html", soup)
    assert links == [
        ("http://example.com/files/a.pdf", "标题甲"),
        ("http://example.com/files/b.pdf", "标题乙"),
    ]


def test_extract_file_links_prefers_title_attribute():
    html = """
    <p>
      公告：<a href="/files/full.pdf" title="中国人民银行公告〔2024〕第2号关于货币政策工具的公告">中国人民银行公告〔2024〕第2号...</a>
    </p>
    """
    soup = _make_soup(html)
    links = pbc_monitor.extract_file_links("http://example.com/list/index.html", soup)
    assert links == [
        (
            "http://example.com/files/full.pdf",
            "中国人民银行公告〔2024〕第2号关于货币政策工具的公告",
        )
    ]


def test_extract_pagination_links():
    html = """
    <html><body>
      <a href="index.html">1</a>
      <a href="index_1.html">下一页</a>
      <a href="index_3.html">3</a>
      <a href="/zhengwugongkai/4081330/4406346/4406348/index_5.html">尾页</a>
    </body></html>
    """
    soup = _make_soup(html)
    pages = pbc_monitor.extract_pagination_links(
        "http://www.pbc.gov.cn/zhengwugongkai/4081330/4406346/4406348/index.html",
        soup,
        "http://www.pbc.gov.cn/zhengwugongkai/4081330/4406346/4406348/index.html",
    )
    assert "http://www.pbc.gov.cn/zhengwugongkai/4081330/4406346/4406348/index_1.html" in pages
    assert "http://www.pbc.gov.cn/zhengwugongkai/4081330/4406346/4406348/index_3.html" in pages


def test_state_roundtrip():
    with tempfile.TemporaryDirectory() as tmpdir:
        state_path = os.path.join(tmpdir, "pbc_state.json")
        entries = {
            "http://example.com/a.pdf": "公告A",
            "http://example.com/b.pdf": "",
        }
        pbc_monitor.save_state(state_path, entries)
        with open(state_path, "r", encoding="utf-8") as handle:
            stored = json.load(handle)
        assert stored == [
            {"url": "http://example.com/a.pdf", "name": "公告A"},
            {"url": "http://example.com/b.pdf", "name": ""},
        ]
        loaded = pbc_monitor.load_state(state_path)
        assert loaded == entries


def test_load_state_from_legacy_list():
    with tempfile.TemporaryDirectory() as tmpdir:
        state_path = os.path.join(tmpdir, "state.json")
        legacy = ["http://example.com/a.pdf", "http://example.com/b.pdf"]
        with open(state_path, "w", encoding="utf-8") as handle:
            json.dump(legacy, handle)
        loaded = pbc_monitor.load_state(state_path)
        assert loaded == {
            "http://example.com/a.pdf": "",
            "http://example.com/b.pdf": "",
        }


def test_fetch_uses_apparent_encoding_for_iso8859():
    class FakeResponse:
        def __init__(self):
            self.encoding = "ISO-8859-1"
            self.apparent_encoding = "gbk"
            self._content = "名称".encode("gbk")

        def raise_for_status(self):
            return None

        @property
        def text(self):
            return self._content.decode(self.encoding, errors="strict")

    class FakeSession:
        def get(self, url, timeout):
            return FakeResponse()

    result = pbc_monitor._fetch(FakeSession(), "http://example.com", 0.0, 0.0, 10.0)
    assert result == "名称"


def test_compute_sleep_seconds_range():
    seconds = [pbc_monitor._compute_sleep_seconds(1, 2) for _ in range(10)]
    for value in seconds:
        assert 3600 <= value <= 7200


def test_collect_new_files_saves_state_on_each_download():
    html = """
    <html><body>
      <a href="file1.pdf">文件一</a>
      <a href="file2.pdf">文件二</a>
    </body></html>
    """

    def fake_iterate(session, start_url, delay, jitter, timeout):
        yield start_url, _make_soup(html)

    download_calls = []

    def fake_download_file(session, file_url, output_dir, delay, jitter, timeout):
        download_calls.append(file_url)
        os.makedirs(output_dir, exist_ok=True)
        if file_url.endswith("file2.pdf"):
            raise RuntimeError("fail second download")
        return os.path.join(output_dir, os.path.basename(file_url))

    save_calls = []
    skip_messages = []
    original_iterate = pbc_monitor.iterate_listing_pages
    original_download = pbc_monitor.download_file
    original_save = pbc_monitor.save_state
    original_print = builtins.print
    try:
        pbc_monitor.iterate_listing_pages = fake_iterate
        pbc_monitor.download_file = fake_download_file

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = os.path.join(tmpdir, "state.json")

            def wrapped_save_state(path, urls):
                save_calls.append((path, sorted(urls)))
                original_save(path, urls)

            pbc_monitor.save_state = wrapped_save_state

            def fake_print(*args, **kwargs):
                message = " ".join(str(arg) for arg in args)
                skip_messages.append(message)

            builtins.print = fake_print

            known = {}
            downloaded = pbc_monitor.collect_new_files(
                session=None,
                start_url="http://example.com/index.html",
                output_dir=os.path.join(tmpdir, "out"),
                known_entries=known,
                delay=0.0,
                jitter=0.0,
                timeout=10.0,
                state_file=state_path,
            )

            assert downloaded == [os.path.join(tmpdir, "out", "file1.pdf")]
            assert download_calls == [
                "http://example.com/file1.pdf",
                "http://example.com/file2.pdf",
            ]
            assert save_calls
            first_call = save_calls[0]
            assert first_call[0] == state_path
            assert first_call[1] == [
                "http://example.com/file1.pdf",
            ]

            with open(state_path, "r", encoding="utf-8") as handle:
                data = json.load(handle)
            assert data == [
                {"url": "http://example.com/file1.pdf", "name": "文件一"}
            ]
            assert known["http://example.com/file1.pdf"] == "文件一"

            skip_messages.clear()
            pbc_monitor.collect_new_files(
                session=None,
                start_url="http://example.com/index.html",
                output_dir=os.path.join(tmpdir, "out"),
                known_entries=known,
                delay=0.0,
                jitter=0.0,
                timeout=10.0,
                state_file=state_path,
            )
            assert any("Skipping existing file" in msg for msg in skip_messages)
    finally:
        pbc_monitor.iterate_listing_pages = original_iterate
        pbc_monitor.download_file = original_download
        pbc_monitor.save_state = original_save
        builtins.print = original_print


def test_collect_new_files_updates_missing_name():
    html = """
    <html><body>
      <a href="file1.pdf">文件一</a>
    </body></html>
    """

    def fake_iterate(session, start_url, delay, jitter, timeout):
        yield start_url, _make_soup(html)

    original_iterate = pbc_monitor.iterate_listing_pages
    original_save = pbc_monitor.save_state
    original_print = builtins.print
    messages = []

    try:
        pbc_monitor.iterate_listing_pages = fake_iterate
        def fake_save(path, urls):
            messages.append((path, dict(urls)))
            return original_save(path, urls)

        pbc_monitor.save_state = fake_save

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = os.path.join(tmpdir, "state.json")
            known = {"http://example.com/file1.pdf": ""}
            def capture_print(*args, **kwargs):
                messages.append(" ".join(str(a) for a in args))

            builtins.print = capture_print

            pbc_monitor.collect_new_files(
                session=None,
                start_url="http://example.com/index.html",
                output_dir=os.path.join(tmpdir, "out"),
                known_entries=known,
                delay=0.0,
                jitter=0.0,
                timeout=10.0,
                state_file=state_path,
            )

            assert known["http://example.com/file1.pdf"] == "文件一"
            assert any("Updated name for existing file" in msg for msg in messages if isinstance(msg, str))
    finally:
        pbc_monitor.iterate_listing_pages = original_iterate
        pbc_monitor.save_state = original_save
        builtins.print = original_print
