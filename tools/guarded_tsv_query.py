"""Safe, explicit-column inspection of mixed sealed/unsealed TSV sources."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import TextIO

from tools.vmanus_experiment import GuardedTSV, ROOT


def resolve_repo_file(value: str) -> Path:
    candidate = Path(value)
    path = candidate.resolve() if candidate.is_absolute() else (ROOT / candidate).resolve()
    try:
        path.relative_to(ROOT)
    except ValueError as exc:
        raise ValueError("query path must remain inside the repository") from exc
    if not path.is_file():
        raise ValueError(f"query source is not a file: {path}")
    return path


def query(
    *,
    path: Path,
    selector: str,
    allowed_values: set[str],
    columns: list[str],
    forbidden_prefixes: tuple[str, ...] = ("f84",),
    count_only: bool = False,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
) -> int:
    stdout = stdout or sys.stdout
    stderr = stderr or sys.stderr
    if not allowed_values:
        raise ValueError("at least one explicit --allow selector value is required")
    if not columns:
        raise ValueError("at least one output column is required")
    if len(columns) != len(set(columns)):
        raise ValueError("output columns must be unique")

    with path.open(encoding="utf-8", newline="") as handle:
        header_line = handle.readline()
    if not header_line:
        raise ValueError("query source is empty")
    header = next(csv.reader([header_line], delimiter="\t"))
    missing = [column for column in [selector, *columns] if column not in header]
    if missing:
        raise ValueError("missing TSV columns: " + ", ".join(missing))

    source = GuardedTSV(
        path,
        selector_column=selector,
        allowed_values=allowed_values,
        forbidden_prefixes=forbidden_prefixes,
        forbidden_action="skip",
    )
    rows = list(source)
    if count_only:
        print(
            json.dumps(
                {
                    "selected": len(rows),
                    "skipped_forbidden": source.stats.skipped_forbidden,
                    "skipped_not_allowed": source.stats.skipped_not_allowed,
                },
                sort_keys=True,
            ),
            file=stdout,
        )
    else:
        writer = csv.DictWriter(
            stdout,
            fieldnames=columns,
            delimiter="\t",
            lineterminator="\n",
            extrasaction="ignore",
        )
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row[column] for column in columns})
        print(
            "GUARD_STATS "
            + json.dumps(
                {
                    "selected": len(rows),
                    "skipped_forbidden": source.stats.skipped_forbidden,
                    "skipped_not_allowed": source.stats.skipped_not_allowed,
                },
                sort_keys=True,
            ),
            file=stderr,
        )
    return 0
