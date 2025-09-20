import os
import sys
import types
import urllib.parse

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

requests_stub = types.SimpleNamespace()
requests_stub.compat = types.SimpleNamespace(urljoin=urllib.parse.urljoin)
requests_stub.get = lambda url: None
sys.modules["requests"] = requests_stub

bs4_stub = types.SimpleNamespace()

class _Tag:
    def __init__(self, href: str):
        self._href = href

    def __getitem__(self, key: str) -> str:
        return self._href


class _Soup:
    def __init__(self, text: str, parser: str):
        self._text = text

    def find_all(self, tag: str, href: bool = False):
        return []


bs4_stub.BeautifulSoup = _Soup
sys.modules["bs4"] = bs4_stub

pdfkit_stub = types.SimpleNamespace(from_url=lambda *a, **k: None)
sys.modules["pdfkit"] = pdfkit_stub

from icrawler.crawler import safe_filename


def test_safe_filename():
    assert safe_filename('http://example.com/a?b=1') == 'http___example_com_a_b_1'
    assert safe_filename('中国人民银行公告[2010]第17号') == '中国人民银行公告_2010_第17号'
