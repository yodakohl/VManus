"""Compact experiment navigation, reading only the generated metadata index.

Returned paths are navigation hints, not files opened by this helper. In
particular, lookup does not read manifests, reports, manuscript data or images,
and a listed path never grants permission to open sealed content.
"""

from __future__ import annotations

import csv
import json
import re
from collections import Counter
from collections.abc import Sequence
from pathlib import Path, PurePosixPath

from tools.vmanus_experiment import ROOT


ID_RE = re.compile(r"GDT([0-9]+)", re.IGNORECASE)
REQUIRED_COLUMNS = {"experiment_id", "question", "status", "primary_report"}


def normalize_id(value: str) -> str:
    match = ID_RE.fullmatch(value.strip())
    if match is None or int(match[1]) == 0:
        raise ValueError(f"invalid experiment ID: {value!r}; expected GDT followed by a positive integer")
    return f"GDT{int(match[1]):03d}"


def _paths(row: dict[str, str], *columns: str) -> list[str]:
    return sorted({path for column in columns for path in row.get(column, "").split(";") if path})


def _preferred(paths: list[str], names: Sequence[str]) -> str:
    for name in names:
        matches = [path for path in paths if PurePosixPath(path).name.lower() == name.lower()]
        if matches:
            return min(matches, key=lambda path: (len(PurePosixPath(path).parts), path))
    return ""


def _entrypoints(row: dict[str, str]) -> dict[str, str]:
    """Select bounded conventional pointers; never guess a main script among many."""
    documents = _paths(row, "methods", "reports")
    scripts = _paths(row, "runners", "validators")
    validators = [path for path in scripts if PurePosixPath(path).name.lower().startswith("validate")]
    runners = [path for path in scripts if path not in validators]
    all_outputs = sorted(set(documents + _paths(row, "artifacts")))
    readers = [
        path for path in all_outputs
        if any(term in PurePosixPath(path).name.upper() for term in ("FULL_TEXT", "PARAGRAPH_READINGS", "LINE_READER"))
    ]
    readers.sort(key=lambda path: (
        next(index for index, term in enumerate(("FULL_TEXT", "PARAGRAPH_READINGS", "LINE_READER"))
             if term in PurePosixPath(path).name.upper()),
        path,
    ))
    values = {
        "working_theory": _preferred(documents, ["WORKING_THEORY.md"]),
        "reader": readers[0] if readers else "",
        "method": _preferred(documents, ["METHOD.md", f"{row['experiment_id']}_METHOD.md"]),
        "preregistration": _preferred(documents, ["PREREGISTRATION.md"]),
        "runner": _preferred(runners, ["run.py", "run_experiment.py"]) or (runners[0] if len(runners) == 1 else ""),
        "validator": _preferred(validators, ["validate.py", "validate_experiment.py"]) or (validators[0] if len(validators) == 1 else ""),
        "manifest": row.get("manifest", ""),
    }
    return {name: value for name, value in values.items() if value}


def lookup_experiments(
    identifiers: Sequence[str], *, index_path: Path | None = None
) -> list[dict[str, object]]:
    """Return requested-order cards from the index, or fail without partial output.

    ``index_path`` is for metadata fixtures and library callers; the CLI always
    uses the repository index. Duplicate IDs, including case/padding aliases,
    are errors both in the request and in the index.
    """
    if not identifiers:
        raise ValueError("at least one experiment ID is required")
    requested = [normalize_id(value) for value in identifiers]
    duplicates = sorted(key for key, count in Counter(requested).items() if count > 1)
    if duplicates:
        raise ValueError("duplicate experiment IDs requested: " + ", ".join(duplicates))
    wanted = set(requested)
    found: dict[str, dict[str, object]] = {}
    seen: set[str] = set()
    index_duplicates: set[str] = set()
    path = index_path if index_path is not None else ROOT / "experiments/EXPERIMENT_INDEX.tsv"
    try:
        with path.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle, delimiter="\t")
            missing = sorted(REQUIRED_COLUMNS - set(reader.fieldnames or []))
            if missing:
                raise ValueError("experiment index missing columns: " + ", ".join(missing))
            for row in reader:
                if None in row or any(value is None for value in row.values()):
                    raise ValueError(f"malformed experiment index row at line {reader.line_num}")
                identifier = normalize_id(row["experiment_id"])
                if identifier in seen:
                    index_duplicates.add(identifier)
                seen.add(identifier)
                if identifier not in wanted:
                    continue
                row["experiment_id"] = identifier
                found[identifier] = {
                    "experiment_id": identifier,
                    "question": row["question"],
                    "status": row["status"],
                    "primary_report": row["primary_report"],
                    "entrypoints": _entrypoints(row),
                }
    except OSError as exc:
        raise ValueError(f"cannot read experiment index ({type(exc).__name__})") from exc
    except csv.Error as exc:
        raise ValueError(f"cannot parse experiment index: {exc}") from exc
    if index_duplicates:
        raise ValueError("duplicate experiment IDs in index: " + ", ".join(sorted(index_duplicates)))
    unknown = sorted(wanted - found.keys())
    if unknown:
        raise ValueError("unknown experiment IDs: " + ", ".join(unknown))
    return [found[identifier] for identifier in requested]


def render_lookup(rows: list[dict[str, object]], *, json_output: bool = False) -> str:
    if json_output:
        return json.dumps(rows, ensure_ascii=False, indent=2) + "\n"
    cards: list[str] = []
    for row in rows:
        lines = [str(row["experiment_id"])]
        for name in ("question", "status", "primary_report"):
            value = " ".join(str(row[name]).split()) or "[not recorded in index]"
            lines.append(f"  {name}: {value}")
        for name, value in row["entrypoints"].items():
            lines.append(f"  {name}: {' '.join(value.split())}")
        cards.append("\n".join(lines))
    return "\n\n".join(cards) + "\n"
