import os
import sys
import types
import urllib.parse
import re

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

requests_stub = types.SimpleNamespace()
requests_stub.compat = types.SimpleNamespace(urljoin=urllib.parse.urljoin)
requests_stub.get = lambda url: None
sys.modules["requests"] = requests_stub

class _Tag:
    def __init__(self, href: str):
        self._href = href

    def __getitem__(self, key: str) -> str:
        return self._href


class _Soup:
    def __init__(self, text: str, parser: str):
        self._text = text

    def find_all(self, tag: str, href: bool = False):
        return [_Tag(h) for h in re.findall(r'href="(.*?)"', self._text)]


bs4_stub = types.SimpleNamespace(BeautifulSoup=_Soup)
sys.modules["bs4"] = bs4_stub

pdfkit_stub = types.SimpleNamespace(from_url=lambda *a, **k: None)
sys.modules["pdfkit"] = pdfkit_stub
import importlib
import pbc_regulations.icrawler.crawler as crawler
importlib.reload(crawler)
from pbc_regulations.icrawler.crawler import crawl

class DummyResponse:
    def __init__(self, text=""):
        self.text = text
        self.content = b""
    def raise_for_status(self):
        pass


def test_crawl_respects_delay(tmp_path, monkeypatch):
    html = '<a href="file.pdf">pdf</a>'
    monkeypatch.setattr("pbc_regulations.icrawler.crawler.requests.get", lambda url: DummyResponse(html))
    monkeypatch.setattr("pbc_regulations.icrawler.crawler.download_file", lambda url, out: None)
    monkeypatch.setattr("pbc_regulations.icrawler.crawler.save_page_as_pdf", lambda url, out: None)
    sleeps = []
    monkeypatch.setattr("pbc_regulations.icrawler.crawler.time.sleep", lambda s: sleeps.append(s))
    monkeypatch.setattr("pbc_regulations.icrawler.crawler.random.uniform", lambda a, b: b)
    crawl(["http://example.com"], tmp_path, delay=1, jitter=0.5)
    assert sleeps == [1.5, 1.5]
