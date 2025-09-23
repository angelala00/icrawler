import json
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from searcher.api_server import create_app  # noqa: E402
from searcher.policy_finder import PolicyFinder  # noqa: E402


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
def api_client(sample_state_files):
    policy_path, notice_path = sample_state_files
    finder = PolicyFinder(str(policy_path), str(notice_path))
    app = create_app(finder)
    with TestClient(app) as client:
        yield client


def test_get_search_endpoint(api_client):
    response = api_client.get(
        "/search",
        params={"query": "人民银行公告", "topk": "2"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["query"] == "人民银行公告"
    assert payload["result_count"] >= 1
    result = payload["results"][0]
    assert result["title"].startswith("中国人民银行公告")
    assert "documents" in result
    assert result["score"] > 0


def test_post_search_without_documents(api_client):
    response = api_client.post(
        "/search",
        json={
            "query": "监管",
            "topk": 2,
            "include_documents": False,
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["result_count"] == 2
    for result in payload["results"]:
        assert "documents" not in result


def test_missing_query_returns_error(api_client):
    response = api_client.get("/search")
    assert response.status_code == 400
    payload = response.json()
    assert payload["error"]
    assert "query" in payload["error"]
