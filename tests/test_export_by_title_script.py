from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_export_by_title_script_invocation(tmp_path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    script_path = repo_root / "scripts" / "export_by_title.py"

    source_file = tmp_path / "source.txt"
    source_file.write_text("example content", encoding="utf-8")

    state_file = tmp_path / "state.json"
    state_data = {
        "entries": [
            {
                "serial": 1,
                "title": "Example Entry",
                "remark": "",
                "documents": [
                    {
                        "url": "https://example.com/document",
                        "type": "pdf",
                        "title": "Example Document",
                        "downloaded": True,
                        "local_path": str(source_file),
                    }
                ],
            }
        ]
    }
    state_file.write_text(json.dumps(state_data), encoding="utf-8")

    output_dir = tmp_path / "output"

    result = subprocess.run(
        [
            sys.executable,
            str(script_path),
            str(state_file),
            str(output_dir),
            "--dry-run",
        ],
        capture_output=True,
        check=True,
        text=True,
    )

    assert "Total files planned" in result.stdout
