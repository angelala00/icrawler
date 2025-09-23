import json
import sys
import threading
import time
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen

import pytest


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from searcher.api_server import build_server
from searcher.policy_finder import PolicyFinder


@pytest.fixture
def sample_state_files(tmp_path):
    policy_updates = {
        "entries": [
            {
                "serial": 1,
                "title": "中国人民银行公告〔2023〕第3号 关于测试",
                "remark": "测试备注",
                "documents": [
                    {"type": "pdf", "local_path": "/tmp/policy.pdf"},
                    {"type": "html", "local_path": "/tmp/policy.html"},
                ],
            }
        ]
    }
    regulator_notice = {
        "entries": [
            {
                "serial": 2,
                "title": "监管问答 2021 年度总结",
                "remark": "年度总结",
                "documents": [
                    {"type": "pdf", "local_path": "/tmp/notice.pdf"},
                ],
            }
        ]
    }
    policy_path = tmp_path / "policy_updates.json"
    notice_path = tmp_path / "regulator_notice.json"
    policy_path.write_text(json.dumps(policy_updates, ensure_ascii=False), "utf-8")
    notice_path.write_text(json.dumps(regulator_notice, ensure_ascii=False), "utf-8")
    return policy_path, notice_path


@pytest.fixture
def running_server(sample_state_files):
    policy_path, notice_path = sample_state_files
    finder = PolicyFinder(str(policy_path), str(notice_path))
    server = build_server(finder, "127.0.0.1", 0)
    host, port = server.server_address[:2]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base_url = f"http://{host}:{port}"

    # Wait briefly to ensure the server thread is listening.
    time.sleep(0.05)

    yield base_url

    server.shutdown()
    thread.join(timeout=1)
    server.server_close()


def test_get_search_endpoint(running_server):
    encoded_query = quote("人民银行公告")
    response = urlopen(f"{running_server}/search?query={encoded_query}&topk=2")
    payload = json.loads(response.read().decode("utf-8"))
    assert payload["query"] == "人民银行公告"
    assert payload["result_count"] >= 1
    result = payload["results"][0]
    assert result["title"].startswith("中国人民银行公告")
    assert "documents" in result
    assert result["score"] > 0


def test_post_search_without_documents(running_server):
    request = Request(
        f"{running_server}/search",
        data=json.dumps({
            "query": "监管",
            "topk": 2,
            "include_documents": False,
        }).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    response = urlopen(request)
    payload = json.loads(response.read().decode("utf-8"))
    assert payload["result_count"] == 2
    for result in payload["results"]:
        assert "documents" not in result


def test_missing_query_returns_error(running_server):
    with pytest.raises(HTTPError) as excinfo:
        urlopen(f"{running_server}/search")
    body = excinfo.value.read().decode("utf-8")
    payload = json.loads(body)
    assert payload["error"]
    assert "query" in payload["error"]
