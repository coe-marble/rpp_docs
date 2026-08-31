#!/usr/bin/env python3
"""Validate the RPP documentation catalog against an rpp_dev checkout."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


def catalog_ids(catalog: Path) -> list[tuple[str, str]]:
    entries: list[tuple[str, str]] = []
    current_id = current_path = None
    for line in catalog.read_text(encoding="utf-8").splitlines():
        if line.startswith("  - id: "):
            if current_id and current_path:
                entries.append((current_id, current_path))
            current_id = line.removeprefix("  - id: ").strip()
            current_path = None
        elif line.startswith("    path: "):
            current_path = line.removeprefix("    path: ").strip()
    if current_id and current_path:
        entries.append((current_id, current_path))
    return entries


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, default=Path(".."))
    parser.add_argument(
        "--catalog",
        type=Path,
        default=Path(__file__).parents[1] / "docs" / "repositories.yml",
    )
    args = parser.parse_args()
    workspace = args.workspace.expanduser().resolve()
    entries = catalog_ids(args.catalog)
    if not entries:
        print(f"No repositories found in {args.catalog}", file=sys.stderr)
        return 2

    failures = []
    for repository_id, relative_path in entries:
        repository_path = workspace / relative_path
        if not repository_path.is_dir():
            failures.append(f"{repository_id}: missing directory {repository_path}")

    if failures:
        print("Repository catalog check failed:", file=sys.stderr)
        print("\n".join(f"- {failure}" for failure in failures), file=sys.stderr)
        return 1
    print(f"Repository catalog is valid ({len(entries)} repositories).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())