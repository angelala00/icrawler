"""Copy downloaded files using their title metadata as filenames."""

from __future__ import annotations

import argparse
from pathlib import Path

from icrawler.export_titles import copy_documents_by_title


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "state_file",
        nargs="?",
        default="artifacts/downloads/default_state.json",
        help="path to state.json (default: %(default)s)",
    )
    parser.add_argument(
        "output_dir",
        help="directory where renamed copies should be written",
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

    report, plans = copy_documents_by_title(
        Path(args.state_file),
        Path(args.output_dir),
        dry_run=args.dry_run,
        overwrite=args.overwrite,
    )

    prefix = "[DRY RUN] Would copy" if args.dry_run else "Copied"
    for plan in plans:
        print(f"{prefix}: {plan.source} -> {plan.destination}")

    print(f"Total files planned: {report.copied}")
    if report.skipped_missing_source:
        print(f"Missing source files: {report.skipped_missing_source}")
    if report.skipped_without_path:
        print(f"Entries without a local path: {report.skipped_without_path}")


if __name__ == "__main__":
    main()

