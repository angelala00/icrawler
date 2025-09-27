"""Copy downloaded files using their title metadata as filenames.

This helper can export documents for a single state file or discover
state files for every configured task and export them into per-task
subdirectories.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Tuple

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from pbc_regulations.icrawler.crawler import safe_filename
from pbc_regulations.icrawler.export_titles import copy_documents_by_title
from pbc_regulations.icrawler import pbc_monitor


@dataclass
class TaskExportPlan:
    """Information required to export files for a single task."""

    display_name: str
    state_file: Path
    slug: str


def _resolve_project_path(path: Path) -> Path:
    """Return an absolute path relative to the project root."""

    if path.is_absolute():
        return path
    return (REPO_ROOT / path).resolve()


def _slugify(name: str, *, fallback: Optional[str] = None) -> str:
    """Generate a filesystem-friendly slug for *name*."""

    candidates: Iterable[str] = (name,) if fallback is None else (name, fallback)
    for candidate in candidates:
        if not candidate:
            continue
        slug = safe_filename(candidate).strip("_")
        if slug:
            return slug
    return "task"


def _assign_unique_slug(slug: str, used: Dict[str, int]) -> str:
    """Ensure *slug* is unique by appending a numeric suffix when needed."""

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
) -> Tuple[List[TaskExportPlan], Path]:
    """Return discovered export plans and the artifact directory used."""

    config = pbc_monitor.load_config(config_path)

    artifact_setting = artifact_dir_override or config.get("artifact_dir") or "artifacts"
    artifact_dir = Path(str(artifact_setting)).expanduser()
    if not artifact_dir.is_absolute():
        artifact_dir = _resolve_project_path(artifact_dir)

    plans: List[TaskExportPlan] = []
    seen_paths: Dict[Path, TaskExportPlan] = {}

    tasks = config.get("tasks") if isinstance(config, dict) else None
    if isinstance(tasks, list):
        for index, raw_task in enumerate(tasks):
            if not isinstance(raw_task, dict):
                continue
            display_name = str(raw_task.get("name") or f"task{index + 1}")
            slug = _slugify(display_name)
            default_state_filename = f"{slug}_state.json"
            state_value = pbc_monitor._select_task_value(None, raw_task, config, "state_file")
            resolved_state = pbc_monitor._resolve_artifact_path(
                state_value if isinstance(state_value, str) else None,
                str(artifact_dir),
                "downloads",
                default_basename=default_state_filename,
            )
            if not resolved_state:
                continue
            state_path = Path(resolved_state)
            plans.append(TaskExportPlan(display_name, state_path, slug))
            seen_paths[state_path.resolve()] = plans[-1]

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
            plan = TaskExportPlan(name, state_path, slug)
            plans.append(plan)
            seen_paths[resolved] = plan

    if not plans:
        default_state = artifact_dir / "downloads" / "default_state.json"
        plans.append(TaskExportPlan("default", default_state, _slugify("default")))

    return plans, artifact_dir


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "state_file",
        nargs="?",
        default=None,
        help="path to state.json; when omitted the script discovers state files",
    )
    parser.add_argument(
        "output_dir",
        help="directory where renamed copies should be written",
    )
    parser.add_argument(
        "--config",
        default="pbc_config.json",
        help=(
            "path to configuration file used for auto-discovery "
            "when state_file is not provided (default: %(default)s)"
        ),
    )
    parser.add_argument(
        "--artifact-dir",
        help="override artifact directory for auto-discovery",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="overwrite files in the output directory instead of adding suffixes",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="show the planned copies without writing any files",
    )
    args = parser.parse_args()

    if args.state_file:
        base_output = Path(args.output_dir)
        plans = [
            TaskExportPlan(
                display_name=Path(args.state_file).stem,
                state_file=Path(args.state_file),
                slug=_slugify(Path(args.state_file).stem),
            )
        ]
    else:
        plans, artifact_dir = _discover_task_plans(
            config_path=args.config,
            artifact_dir_override=args.artifact_dir,
        )
        print(f"Discovered {len(plans)} task(s) from {artifact_dir}")
        base_output = Path(args.output_dir)

    used_slugs: Dict[str, int] = {}
    for task_plan in plans:
        if args.state_file:
            destination = base_output
        else:
            slug = _assign_unique_slug(task_plan.slug, used_slugs)
            destination = base_output / slug

        print(
            f"\n=== Task: {task_plan.display_name} ===\n"
            f"State file: {task_plan.state_file}\n"
            f"Output directory: {destination}"
        )

        report, copies = copy_documents_by_title(
            task_plan.state_file,
            destination,
            dry_run=args.dry_run,
            overwrite=args.overwrite,
        )

        prefix = "[DRY RUN] Would copy" if args.dry_run else "Copied"
        for plan in copies:
            print(f"{prefix}: {plan.source} -> {plan.destination}")

        print(f"Total files planned: {report.copied}")
        if report.skipped_missing_source:
            print(f"Missing source files: {report.skipped_missing_source}")
        if report.skipped_without_path:
            print(f"Entries without a local path: {report.skipped_without_path}")


if __name__ == "__main__":
    main()
