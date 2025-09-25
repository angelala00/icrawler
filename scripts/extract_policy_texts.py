"""Generate plain-text files for each entry in a state JSON file.

This helper now supports two workflows:

* When a ``state_file`` argument is supplied it behaves like the
  original version – writing extracted text files next to the provided
  state JSON (unless overridden via ``--output-dir``) and saving the
  updated state structure.
* When executed without positional arguments the script discovers all
  available task state files using the crawler configuration and writes
  the generated text files to ``<artifact_dir>/extract/<task>/``.  A
  companion summary JSON (``extract_<task>.json``) is produced with
  per-entry metadata including the generated text path.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from icrawler import pbc_monitor
from icrawler.crawler import safe_filename

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


def run(state_path: Path, output_dir: Path, output_state_path: Path) -> Tuple[ProcessReport, Dict[str, Any]]:
    data: Dict[str, Any] = json.loads(state_path.read_text(encoding="utf-8"))
    report = process_state_data(data, output_dir, state_path=state_path)
    output_state_path.parent.mkdir(parents=True, exist_ok=True)
    output_state_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return report, data


@dataclass
class TaskPlan:
    display_name: str
    state_file: Path
    slug: str


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _resolve_project_path(path: Path) -> Path:
    if path.is_absolute():
        return path
    return (_repo_root() / path).resolve()


def _slugify(name: str, *, fallback: Optional[str] = None) -> str:
    candidates: Iterable[str] = (name,) if fallback is None else (name, fallback)
    for candidate in candidates:
        if not candidate:
            continue
        slug = safe_filename(candidate).strip("_")
        if slug:
            return slug
    return "task"


def _assign_unique_slug(slug: str, used: Dict[str, int]) -> str:
    count = used.get(slug, 0)
    if count == 0:
        used[slug] = 1
        return slug
    new_count = count + 1
    used[slug] = new_count
    return f"{slug}_{new_count}"


def _discover_task_plans(
    *,
    config_path: Optional[str],
    artifact_dir_override: Optional[str],
    selected_tasks: Optional[Iterable[str]] = None,
) -> Tuple[List[TaskPlan], Path]:
    config = pbc_monitor.load_config(config_path)

    artifact_setting = artifact_dir_override or config.get("artifact_dir") or "artifacts"
    artifact_dir = Path(str(artifact_setting)).expanduser()
    if not artifact_dir.is_absolute():
        artifact_dir = _resolve_project_path(artifact_dir)

    selected: Optional[Set[str]]
    if selected_tasks:
        normalized: Set[str] = set()
        for task in selected_tasks:
            if not task:
                continue
            normalized.add(task)
            normalized.add(task.lower())
            slug = safe_filename(task).strip("_")
            if slug:
                normalized.add(slug)
                normalized.add(slug.lower())
        selected = normalized
    else:
        selected = None

    plans: List[TaskPlan] = []
    seen_paths: Dict[Path, TaskPlan] = {}

    tasks = config.get("tasks") if isinstance(config, dict) else None
    if isinstance(tasks, list):
        for index, raw_task in enumerate(tasks):
            if not isinstance(raw_task, dict):
                continue
            display_name = str(raw_task.get("name") or f"task{index + 1}")
            slug = _slugify(display_name)
            if selected and slug not in selected and slug.lower() not in selected and display_name not in selected and display_name.lower() not in selected:
                continue
            default_state_filename = f"{slug}_state.json"
            state_value = pbc_monitor._select_task_value(None, raw_task, config, "state_file")
            resolved_state = pbc_monitor._resolve_artifact_path(
                state_value if isinstance(state_value, str) else None,
                str(artifact_dir),
                "downloads",
                task_name=slug,
                default_basename=default_state_filename,
            )
            if not resolved_state:
                continue
            state_path = Path(resolved_state)
            if not state_path.exists():
                legacy_state = artifact_dir / "downloads" / default_state_filename
                if legacy_state.exists():
                    state_path = legacy_state
            plan = TaskPlan(display_name=display_name, state_file=state_path, slug=slug)
            plans.append(plan)
            seen_paths[state_path.resolve()] = plan

    downloads_dir = artifact_dir / "downloads"
    if downloads_dir.exists():
        for state_path in sorted(downloads_dir.glob("*_state.json")):
            resolved = state_path.resolve()
            if resolved in seen_paths:
                continue
            name = state_path.stem
            if name.endswith("_state"):
                name = name[: -len("_state")] or name
            slug = _slugify(name, fallback=state_path.stem)
            if selected and slug not in selected and slug.lower() not in selected and name not in selected and name.lower() not in selected:
                continue
            plan = TaskPlan(display_name=name, state_file=state_path, slug=slug)
            plans.append(plan)
            seen_paths[resolved] = plan

    if not plans:
        default_state = artifact_dir / "downloads" / "default_state.json"
        plans.append(TaskPlan("default", default_state, _slugify("default")))

    return plans, artifact_dir


def _build_summary_payload(
    *,
    plan: TaskPlan,
    report: ProcessReport,
    state_data: Dict[str, Any],
    output_dir: Path,
    output_state_path: Path,
) -> Dict[str, Any]:
    entries: List[Dict[str, Any]]
    raw_entries = state_data.get("entries")
    if isinstance(raw_entries, list):
        entries = raw_entries  # type: ignore[assignment]
    else:
        entries = []

    results: List[Dict[str, Any]] = []
    for record in report.records:
        entry_payload: Dict[str, Any] = {
            "entry_index": record.entry_index,
            "serial": record.serial,
            "title": record.title,
            "status": record.status,
            "needs_ocr": record.pdf_needs_ocr,
            "text_path": str(record.text_path),
            "text_filename": record.text_path.name,
        }
        if record.source_type:
            entry_payload["source_type"] = record.source_type
        if record.source_path:
            entry_payload["source_path"] = record.source_path
        if record.entry_index < len(entries):
            entry_payload["entry"] = entries[record.entry_index]
        results.append(entry_payload)

    payload: Dict[str, Any] = {
        "task": plan.display_name,
        "task_slug": plan.slug,
        "state_file": str(plan.state_file),
        "output_state_file": str(output_state_path),
        "text_output_dir": str(output_dir),
        "entries": results,
    }
    return payload


def main() -> None:  # pragma: no cover - exercised via integration tests
    parser = argparse.ArgumentParser(description="从 state.json 中提取文本内容并生成 txt 文件。")
    parser.add_argument("state_file", nargs="?", type=Path, help="原始 state.json 文件路径")
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
    parser.add_argument(
        "--summary",
        type=Path,
        default=None,
        help="提取结果摘要保存路径（默认不生成，仅自动发现模式下会保存）",
    )
    parser.add_argument(
        "--config",
        default="pbc_config.json",
        help="配置文件路径，用于自动发现任务（默认: %(default)s）",
    )
    parser.add_argument(
        "--artifact-dir",
        default=None,
        help="覆盖配置中的 artifact_dir，用于自动发现任务",
    )
    parser.add_argument(
        "--task",
        action="append",
        default=None,
        help="仅处理指定任务（可重复使用），支持任务名称或 slug",
    )
    args = parser.parse_args()

    if args.state_file is not None:
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

        report, state_data = run(state_path, output_dir, output_state_path)
        print(_format_summary(report))

        if args.summary is not None:
            summary_path = args.summary.expanduser().resolve()
            summary_path.parent.mkdir(parents=True, exist_ok=True)
            payload = _build_summary_payload(
                plan=TaskPlan(display_name=state_path.stem, state_file=state_path, slug=_slugify(state_path.stem)),
                report=report,
                state_data=state_data,
                output_dir=output_dir,
                output_state_path=output_state_path,
            )
            summary_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"结果摘要已写入: {summary_path}")
        return

    if args.output_state is not None:
        parser.error("自动发现模式不支持 --output-state 参数，请为单个 state 文件使用该选项。")

    plans, artifact_dir = _discover_task_plans(
        config_path=args.config,
        artifact_dir_override=args.artifact_dir,
        selected_tasks=args.task,
    )
    base_extract_dir = artifact_dir / "extract"
    base_extract_dir.mkdir(parents=True, exist_ok=True)

    print(f"自动发现 {len(plans)} 个任务，artifact_dir: {artifact_dir}")

    summary_root = args.summary.expanduser().resolve() if args.summary is not None else None
    used_slugs: Dict[str, int] = {}
    for plan in plans:
        slug = _assign_unique_slug(plan.slug, used_slugs)
        output_dir = base_extract_dir / slug
        output_dir.mkdir(parents=True, exist_ok=True)

        state_path = plan.state_file.expanduser().resolve()
        if not state_path.exists():
            print(f"跳过任务 {plan.display_name}：state 文件不存在 ({state_path})")
            continue

        output_state_path = _default_output_state_path(state_path)

        if summary_root is None:
            summary_path = base_extract_dir / f"extract_{slug}.json"
        elif summary_root.suffix:
            summary_path = summary_root.with_name(f"{summary_root.stem}_{slug}{summary_root.suffix}")
        else:
            summary_path = summary_root / f"extract_{slug}.json"
        summary_path.parent.mkdir(parents=True, exist_ok=True)

        print("==============================")
        print(f"任务: {plan.display_name} (slug: {slug})")
        print(f"State 文件: {state_path}")
        print(f"文本输出目录: {output_dir}")
        print(f"更新后的 state 文件: {output_state_path}")
        print(f"摘要结果: {summary_path}")
        print("开始提取文本...")

        report, state_data = run(state_path, output_dir, output_state_path)
        payload = _build_summary_payload(
            plan=TaskPlan(plan.display_name, state_path, slug),
            report=report,
            state_data=state_data,
            output_dir=output_dir,
            output_state_path=output_state_path,
        )
        summary_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

        print(_format_summary(report))


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    main()

