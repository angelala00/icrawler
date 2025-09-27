import json
import sys
from pathlib import Path
from typing import Dict

import pytest
from fastapi.responses import JSONResponse


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pbc_regulations.searcher.api_server import create_app  # noqa: E402
from pbc_regulations.searcher.clause_lookup import ClauseLookup  # noqa: E402
from pbc_regulations.searcher.policy_finder import (  # noqa: E402
    DEFAULT_SEARCH_TASKS,
    PolicyFinder,
)


@pytest.fixture
def sample_state_files(tmp_path):
    policy_html = tmp_path / "policy.html"
    html_content = """
<html>
  <body>
    <h1>中国人民银行关于加强银行卡收单业务外包管理的通知</h1>
    <p>第三条 第一款 收单机构应当按照下列要求开展外包管理：</p>
    <p>（一）建立健全外包管理制度并明确责任。</p>
    <p>（二）落实风险评估机制。</p>
    <p>第二款 外包合作应当依法合规。</p>
  </body>
</html>
    """.strip()
    policy_html.write_text(html_content, "utf-8")

    policy_text = tmp_path / "policy.txt"
    policy_text.write_text(
        "中国人民银行关于加强银行卡收单业务外包管理的通知\n"
        "第三条 第一款 收单机构应当按照下列要求开展外包管理：\n"
        "（一）建立健全外包管理制度并明确责任。\n"
        "（二）落实风险评估机制。\n"
        "第二款 外包合作应当依法合规。\n",
        "utf-8",
    )

    state_payloads = {
        "zhengwugongkai_administrative_normative_documents": {
            "entries": [
                {
                    "serial": 1,
                    "title": "中国人民银行公告〔2023〕第3号 关于测试",
                    "remark": "测试备注",
                    "documents": [
                        {"type": "text", "local_path": str(policy_text)},
                        {"type": "html", "local_path": str(policy_html)},
                    ],
                }
            ]
        },
        "zhengwugongkai_chinese_regulations": {
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
        },
        "tiaofasi_national_law": {
            "entries": [
                {
                    "serial": 3,
                    "title": "国家法律 金融稳定法（草案）",
                    "remark": "国家法律草案",
                    "documents": [
                        {"type": "pdf", "local_path": "/tmp/national_law.pdf"},
                    ],
                }
            ]
        },
        "tiaofasi_administrative_regulation": {
            "entries": [
                {
                    "serial": 4,
                    "title": "行政法规 支付清算管理条例",
                    "remark": "行政法规",
                    "documents": [
                        {"type": "pdf", "local_path": "/tmp/admin_reg.pdf"},
                    ],
                }
            ]
        },
        "tiaofasi_departmental_rule": {
            "entries": [
                {
                    "serial": 5,
                    "title": "部门规章 金融控股公司监督管理办法",
                    "remark": "部门规章",
                    "documents": [
                        {"type": "pdf", "local_path": "/tmp/dept_rule.pdf"},
                    ],
                }
            ]
        },
        "tiaofasi_normative_document": {
            "entries": [
                {
                    "serial": 6,
                    "title": "规范性文件 金融科技创新指导意见",
                    "remark": "规范性文件",
                    "documents": [
                        {"type": "pdf", "local_path": "/tmp/norm_doc.pdf"},
                    ],
                }
            ]
        },
    }

    state_paths: Dict[str, Path] = {}
    for task_name, payload in state_payloads.items():
        path = tmp_path / f"{task_name}.json"
        path.write_text(json.dumps(payload, ensure_ascii=False), "utf-8")
        state_paths[task_name] = path

    policy_extract = {
        "entries": [
            {
                "entry": state_payloads[
                    "zhengwugongkai_administrative_normative_documents"
                ]["entries"][0],
                "text_path": str(policy_text),
            }
        ]
    }
    notice_extract = {
        "entries": [
            {
                "entry": state_payloads["zhengwugongkai_chinese_regulations"][
                    "entries"
                ][0],
            }
        ]
    }
    policy_extract_path = (
        tmp_path / "zhengwugongkai_administrative_normative_documents_extract.json"
    )
    notice_extract_path = tmp_path / "zhengwugongkai_chinese_regulations_extract.json"
    policy_extract_path.write_text(
        json.dumps(policy_extract, ensure_ascii=False), "utf-8"
    )
    notice_extract_path.write_text(
        json.dumps(notice_extract, ensure_ascii=False), "utf-8"
    )
    extract_paths = {
        "zhengwugongkai_administrative_normative_documents": policy_extract_path,
        "zhengwugongkai_chinese_regulations": notice_extract_path,
    }
    return state_paths, extract_paths


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
    state_paths, extract_paths = sample_state_files
    ordered_state_paths = [
        str(state_paths[name]) for name in DEFAULT_SEARCH_TASKS if name in state_paths
    ]
    finder = PolicyFinder(*ordered_state_paths)
    lookup = ClauseLookup(list(extract_paths.values()))
    app = create_app(finder, lookup)
    get_route = _get_route(app, "/search", "GET")
    post_route = _get_route(app, "/search", "POST")
    return finder, get_route, post_route


@pytest.fixture
def policy_app(sample_state_files):
    state_paths, extract_paths = sample_state_files
    ordered_state_paths = [
        str(state_paths[name]) for name in DEFAULT_SEARCH_TASKS if name in state_paths
    ]
    finder = PolicyFinder(*ordered_state_paths)
    lookup = ClauseLookup(list(extract_paths.values()))
    app = create_app(finder, lookup)
    return app, finder, lookup


def test_get_search_endpoint(policy_api):
    finder, get_route, _ = policy_api
    assert len(finder.entries) == len(DEFAULT_SEARCH_TASKS)
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


def test_search_covers_additional_tasks(policy_api):
    finder, get_route, _ = policy_api
    response = get_route.endpoint(
        query="金融稳定法",
        q=None,
        topk="3",
        include_documents=None,
        documents=None,
        finder_instance=finder,
    )
    assert isinstance(response, JSONResponse)
    assert response.status_code == 200
    payload = json.loads(response.body.decode("utf-8"))
    assert payload["result_count"] >= 1
    titles = [result["title"] for result in payload["results"]]
    assert any("金融稳定法" in title for title in titles)


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


def test_list_policies_without_query(policy_app):
    app, finder, lookup = policy_app
    route = _get_route(app, "/policies", "GET")
    response = route.endpoint(
        query=None,
        finder_instance=finder,
        clause_lookup_instance=lookup,
    )
    assert isinstance(response, JSONResponse)
    assert response.status_code == 200
    data = json.loads(response.body.decode("utf-8"))
    assert data["result_count"] == len(data["policies"])
    assert data["result_count"] == len(DEFAULT_SEARCH_TASKS)
    titles = [item["title"] for item in data["policies"]]
    assert titles[0].startswith("中国人民银行")


def test_list_policies_with_query(policy_app):
    app, finder, lookup = policy_app
    route = _get_route(app, "/policies", "GET")
    response = route.endpoint(
        query="银行卡",
        finder_instance=finder,
        clause_lookup_instance=lookup,
    )
    assert isinstance(response, JSONResponse)
    assert response.status_code == 200
    data = json.loads(response.body.decode("utf-8"))
    assert data["result_count"] == 1
    assert data["policies"][0]["title"].startswith("中国人民银行")


def test_get_policy_meta(policy_app):
    app, finder, lookup = policy_app
    route = _get_route(app, "/policies/{policy_id}", "GET")
    response = route.endpoint(
        policy_id="1",
        include=None,
        finder_instance=finder,
        clause_lookup_instance=lookup,
    )
    assert isinstance(response, JSONResponse)
    assert response.status_code == 200
    data = json.loads(response.body.decode("utf-8"))
    assert data["policy"]["title"].startswith("中国人民银行")


def test_get_policy_text(policy_app):
    app, finder, lookup = policy_app
    route = _get_route(app, "/policies/{policy_id}", "GET")
    response = route.endpoint(
        policy_id="1",
        include=["text"],
        finder_instance=finder,
        clause_lookup_instance=lookup,
    )
    assert isinstance(response, JSONResponse)
    assert response.status_code == 200
    data = json.loads(response.body.decode("utf-8"))
    assert "text" in data
    assert "外包管理" in data["text"]


def test_get_policy_outline(policy_app):
    app, finder, lookup = policy_app
    route = _get_route(app, "/policies/{policy_id}", "GET")
    response = route.endpoint(
        policy_id="1",
        include=["outline"],
        finder_instance=finder,
        clause_lookup_instance=lookup,
    )
    assert isinstance(response, JSONResponse)
    assert response.status_code == 200
    data = json.loads(response.body.decode("utf-8"))
    outline = data["outline"]
    assert outline
    assert outline[0]["type"] == "article"
    assert outline[0]["children"]
