import asyncio
import json
import sys
from pathlib import Path

import pytest
from fastapi.responses import JSONResponse


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from searcher.api_server import create_app  # noqa: E402
from searcher.policy_finder import PolicyFinder  # noqa: E402


@pytest.fixture
def sample_state_files(tmp_path):
    policy_html = tmp_path / "policy.html"
    policy_html.write_text(
        """
<html>
  <body>
    <h1>中国人民银行关于加强银行卡收单业务外包管理的通知</h1>
    <p>第三条 第一款 收单机构应当按照下列要求开展外包管理：</p>
    <p>（一）建立健全外包管理制度并明确责任。</p>
    <p>（二）落实风险评估机制。</p>
    <p>第二款 外包合作应当依法合规。</p>
  </body>
</html>
        """.strip(),
        "utf-8",
    )
    policy_updates = {
        "entries": [
            {
                "serial": 1,
                "title": "中国人民银行公告〔2023〕第3号 关于测试",
                "remark": "测试备注",
                "documents": [
                    {"type": "html", "local_path": str(policy_html)},
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


def _get_route(app, path: str, method: str):
    for route in app.routes:
        if getattr(route, "path", None) != path:
            continue
        methods = getattr(route, "methods", set())
        if methods and method.upper() in methods:
            return route
    raise AssertionError(f"Route {method} {path} not found")


class _SimpleRequest:
    def __init__(self, body: bytes) -> None:
        self._body = body

    async def body(self) -> bytes:
        return self._body


@pytest.fixture
def policy_api(sample_state_files):
    policy_path, notice_path = sample_state_files
    finder = PolicyFinder(str(policy_path), str(notice_path))
    app = create_app(finder)
    get_route = _get_route(app, "/search", "GET")
    post_route = _get_route(app, "/search", "POST")
    return finder, get_route, post_route


def test_get_search_endpoint(policy_api):
    finder, get_route, _ = policy_api
    response = get_route.endpoint(
        query="人民银行公告",
        q=None,
        topk="2",
        include_documents=None,
        documents=None,
        finder_instance=finder,
    )
    assert isinstance(response, JSONResponse)
    assert response.status_code == 200
    payload = json.loads(response.body.decode("utf-8"))
    assert payload["query"] == "人民银行公告"
    assert payload["result_count"] >= 1
    result = payload["results"][0]
    assert result["title"].startswith("中国人民银行公告")
    assert "documents" in result
    assert result["score"] > 0


def test_get_search_includes_clause(policy_api):
    finder, get_route, _ = policy_api
    response = get_route.endpoint(
        query="中国人民银行公告 第三条第一（一）项",
        q=None,
        topk="1",
        include_documents=None,
        documents=None,
        finder_instance=finder,
    )
    assert isinstance(response, JSONResponse)
    assert response.status_code == 200
    payload = json.loads(response.body.decode("utf-8"))
    assert payload.get("clause_reference") is not None
    clause_ref = payload["clause_reference"]
    assert clause_ref["article"] == 3
    assert clause_ref.get("paragraph") == 1
    assert clause_ref.get("item") == 1
    assert payload["result_count"] == 1
    clause_payload = payload["results"][0].get("clause")
    assert clause_payload is not None
    assert clause_payload.get("article_matched") is True
    assert clause_payload.get("item_matched") is True
    assert "建立健全外包管理制度" in clause_payload.get("item_text", "")


def test_post_search_without_documents(policy_api):
    finder, _, post_route = policy_api
    body = json.dumps(
        {"query": "监管", "topk": 2, "include_documents": False},
        ensure_ascii=False,
    ).encode("utf-8")
    request = _SimpleRequest(body)
    response = asyncio.run(post_route.endpoint(request=request, finder_instance=finder))
    assert isinstance(response, JSONResponse)
    assert response.status_code == 200
    payload = json.loads(response.body.decode("utf-8"))
    assert payload["result_count"] == 2
    for result in payload["results"]:
        assert "documents" not in result


def test_missing_query_returns_error(policy_api):
    finder, get_route, _ = policy_api
    response = get_route.endpoint(
        query=None,
        q=None,
        topk=None,
        include_documents=None,
        documents=None,
        finder_instance=finder,
    )
    assert isinstance(response, JSONResponse)
    assert response.status_code == 400
    payload = json.loads(response.body.decode("utf-8"))
    assert payload["error"]
    assert "query" in payload["error"]
