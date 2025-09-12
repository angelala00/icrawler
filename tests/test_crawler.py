from icrawler.crawler import safe_filename


def test_safe_filename():
    assert safe_filename('http://example.com/a?b=1') == 'http___example_com_a_b_1'
