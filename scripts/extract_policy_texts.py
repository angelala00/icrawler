"""Generate plain-text files for each entry in a state JSON file."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict

if __package__ in {None, ""}:  # pragma: no cover - import guard for direct execution
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from icrawler.text_pipeline import ProcessReport, process_state_data


def _default_output_state_path(state_path: Path) -> Path:
    stem = state_path.stem
    suffix = state_path.suffix or ".json"
    return state_path.with_name(f"{stem}_with_text{suffix}")


def _format_summary(report: ProcessReport) -> str:
    lines = [
        f"已生成 {len(report.records)} 个文本文件。",
    ]
    pdf_with_ocr = report.pdf_needs_ocr
    if pdf_with_ocr:
        lines.append(f"其中 {len(pdf_with_ocr)} 个来源于无法提取文本的 PDF，建议后续进行 OCR 识别：")
        for record in pdf_with_ocr:
            serial = f"{record.serial} - " if record.serial is not None else ""
            lines.append(f"  - {serial}{record.title} -> {record.text_path}")
    else:
        lines.append("所有 PDF 均成功提取到文本内容。")
    return "\n".join(lines)


def run(state_path: Path, output_dir: Path, output_state_path: Path) -> ProcessReport:
    data: Dict[str, Any] = json.loads(state_path.read_text(encoding="utf-8"))
    report = process_state_data(data, output_dir, state_path=state_path)
    output_state_path.parent.mkdir(parents=True, exist_ok=True)
    output_state_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return report


def main() -> None:  # pragma: no cover - exercised via integration tests
    parser = argparse.ArgumentParser(description="从 state.json 中提取文本内容并生成 txt 文件。")
    parser.add_argument("state_file", type=Path, help="原始 state.json 文件路径")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="txt 文件输出目录，默认与 state 同级的 texts/ 目录",
    )
    parser.add_argument(
        "--output-state",
        type=Path,
        default=None,
        help="生成的新 state.json 文件路径，默认在原文件名后追加 _with_text",
    )
    args = parser.parse_args()

    state_path: Path = args.state_file.expanduser().resolve()
    if not state_path.is_file():
        parser.error(f"state 文件不存在: {state_path}")

    output_dir = args.output_dir
    if output_dir is None:
        output_dir = state_path.parent / "texts"
    output_dir = output_dir.expanduser().resolve()

    output_state_path = args.output_state
    if output_state_path is None:
        output_state_path = _default_output_state_path(state_path)
    output_state_path = output_state_path.expanduser().resolve()

    report = run(state_path, output_dir, output_state_path)
    print(_format_summary(report))


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    main()

