from __future__ import annotations

import importlib
import json
import os
import sys
from datetime import datetime, timedelta

sys.modules.pop("bs4", None)
importlib.import_module("bs4")

dashboard = importlib.import_module("icrawler.dashboard")
collect_task_overviews = dashboard.collect_task_overviews
render_dashboard_html = dashboard.render_dashboard_html

from icrawler.crawler import safe_filename
from icrawler.fetching import build_cache_path_for_url
from icrawler.state import PBCState, save_state


def _create_state(state_path: str) -> None:
    state = PBCState()

    entry1 = {"title": "Entry 1", "remark": ""}
    entry_id1 = state.ensure_entry(entry1)
    state.merge_documents(
        entry_id1,
        [
            {
                "url": "http://example.com/doc1.pdf",
                "type": "pdf",
                "title": "Doc 1",
                "downloaded": True,
                "local_path": "doc1.pdf",
            },
            {
                "url": "http://example.com/doc2.pdf",
                "type": "pdf",
                "title": "Doc 2",
                "downloaded": False,
            },
        ],
    )

    entry2 = {"title": "Entry 2", "remark": ""}
    entry_id2 = state.ensure_entry(entry2)
    state.merge_documents(
        entry_id2,
        [
            {
                "url": "http://example.com/doc3.pdf",
                "type": "pdf",
                "title": "Doc 3",
                "downloaded": True,
                "local_path": "doc3.pdf",
            }
        ],
    )

    save_state(state_path, state)


def test_collect_task_overview(tmp_path) -> None:
    artifact_dir = tmp_path / "artifacts"
    downloads_dir = artifact_dir / "downloads"
    task_slug = safe_filename("Demo Task")
    pages_dir = artifact_dir / "pages" / task_slug
    output_dir = downloads_dir / task_slug

    output_dir.mkdir(parents=True)
    pages_dir.mkdir(parents=True)

    state_path = downloads_dir / f"{task_slug}_state.json"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    _create_state(str(state_path))

    base_time = datetime(2023, 1, 1, 8, 0, 0)
    timestamp = base_time.timestamp()
    os.utime(state_path, (timestamp, timestamp))
    expected_time = datetime.fromtimestamp(timestamp)

    start_url = "http://example.com/list/index.html"
    cache_file = build_cache_path_for_url(str(pages_dir), start_url)
    os.makedirs(os.path.dirname(cache_file), exist_ok=True)
    with open(cache_file, "w", encoding="utf-8") as handle:
        handle.write("<html></html>")
    os.utime(cache_file, None)

    with open(pages_dir / "extra.html", "w", encoding="utf-8") as handle:
        handle.write("<html></html>")

    for name in ("file1.pdf", "file2.pdf"):
        with open(output_dir / name, "wb") as handle:
            handle.write(b"data")

    config = {
        "artifact_dir": str(artifact_dir),
        "tasks": [
            {
                "name": "Demo Task",
                "start_url": start_url,
                "min_hours": 12,
                "max_hours": 24,
            }
        ],
    }

    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(config), encoding="utf-8")

    overviews = collect_task_overviews(str(config_path))
    assert len(overviews) == 1
    overview = overviews[0]

    assert overview.name == "Demo Task"
    assert overview.entries_total == 2
    assert overview.documents_total == 3
    assert overview.downloaded_total == 2
    assert overview.pending_total == 1
    assert overview.tracked_files == 3
    assert overview.tracked_downloaded == 2
    assert overview.document_type_counts == {"pdf": 3}
    assert overview.entries_without_documents == 0
    assert overview.state_file.endswith(f"{task_slug}_state.json")
    assert overview.state_last_updated == expected_time
    assert overview.next_run_earliest == expected_time + timedelta(hours=12)
    assert overview.next_run_latest == expected_time + timedelta(hours=24)
    assert overview.pages_cached >= 1
    assert overview.output_files == 2
    assert overview.output_size_bytes == 8
    assert overview.status == "attention"
    assert "pending" in overview.status_reason

    html = render_dashboard_html(overviews, generated_at=expected_time, auto_refresh=10)
    assert "Demo Task" in html
    assert "pending download" in html

