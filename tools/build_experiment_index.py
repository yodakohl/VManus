#!/usr/bin/env python3
"""Build deterministic navigation indexes for GDT experiments.

The index is descriptive only. It reads tracked paths and the authoritative
experiment ledger; it does not open manuscript/transcription payloads or run
scientific code.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "experiments/semantic_assumptions/ACTIVE_EXPERIMENT_LEDGER.tsv"
TSV_OUT = ROOT / "experiments/EXPERIMENT_INDEX.tsv"
MD_OUT = ROOT / "experiments/EXPERIMENT_INDEX.md"
GDT_RE = re.compile(r"(?i)gdt(\d{3,})(?!\d)")
STRUCTURED_RE = re.compile(r"^experiments/yolo/gdt(\d{3,})_[a-z0-9][a-z0-9_-]*/")
STRUCTURED_START = 337


@dataclass
class Experiment:
    number: int
    paths: list[str] = field(default_factory=list)
    dependencies: set[int] = field(default_factory=set)
    ledger_rows: list[dict[str, str]] = field(default_factory=list)
    manifest_path: str = ""
    manifest: dict = field(default_factory=dict)


def git_paths() -> list[str]:
    completed = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        cwd=ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    )
    return sorted(line for line in completed.stdout.splitlines() if line)


def experiment_number(text: str) -> int | None:
    match = GDT_RE.search(text)
    return int(match.group(1)) if match else None


def load_ledger() -> list[dict[str, str]]:
    with LEDGER.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    required = {
        "date",
        "experiment",
        "status",
        "live_scope",
        "forbidden_inference",
        "primary_report",
    }
    if not rows or set(rows[0]) != required:
        raise RuntimeError("unexpected ACTIVE_EXPERIMENT_LEDGER.tsv schema")
    return rows


def classify_paths(paths: list[str]) -> dict[str, list[str]]:
    classes = {"methods": [], "reports": [], "runners": [], "validators": [], "artifacts": []}
    for path in paths:
        name = Path(path).name
        upper = name.upper()
        lower = name.lower()
        if lower.endswith(".py"):
            if lower.startswith("validate_") or "/validate" in lower:
                classes["validators"].append(path)
            else:
                classes["runners"].append(path)
        elif lower.endswith(".md"):
            if "REPORT" in upper or "SUMMARY" in upper or "AUDIT" in upper:
                classes["reports"].append(path)
            else:
                classes["methods"].append(path)
        elif lower.endswith((".tsv", ".json", ".json.gz", ".csv", ".txt")):
            classes["artifacts"].append(path)
    for values in classes.values():
        values.sort()
    return classes


def resolve_report(raw: str, reports: list[str]) -> tuple[str, bool]:
    candidates: list[Path] = []
    if raw:
        candidates.extend(
            [
                ROOT / raw,
                ROOT / "experiments/semantic_assumptions" / raw,
            ]
        )
    candidates.extend(ROOT / path for path in reports)
    seen: set[Path] = set()
    for candidate in candidates:
        if candidate in seen:
            continue
        seen.add(candidate)
        if candidate.is_file():
            return candidate.relative_to(ROOT).as_posix(), True
    return raw, False


def describe_layout(number: int, paths: list[str]) -> str:
    prefix = f"experiments/yolo/gdt{number:03d}"
    if any(path.startswith(prefix) for path in paths):
        return "STRUCTURED_YOLO"
    if any("/" not in path for path in paths):
        return "LEGACY_ROOT"
    return "OTHER_TREE"


def build_experiments(paths: list[str], ledger: list[dict[str, str]]) -> dict[int, Experiment]:
    experiments: dict[int, Experiment] = {}
    for path in paths:
        number = experiment_number(path)
        if number is None:
            continue
        experiments.setdefault(number, Experiment(number)).paths.append(path)
    for row in ledger:
        number = experiment_number(row["experiment"])
        if number is not None:
            experiments.setdefault(number, Experiment(number)).ledger_rows.append(row)

    for experiment in experiments.values():
        manifests = [path for path in experiment.paths if path.endswith("/experiment.json")]
        if len(manifests) > 1:
            raise RuntimeError(f"GDT{experiment.number:03d} has multiple structured manifests")
        if manifests:
            experiment.manifest_path = manifests[0]
            experiment.manifest = json.loads((ROOT / manifests[0]).read_text(encoding="utf-8"))
        for path in experiment.paths:
            if not path.endswith(".py"):
                continue
            text = (ROOT / path).read_text(encoding="utf-8", errors="replace")
            for raw in GDT_RE.findall(text):
                dependency = int(raw)
                if dependency != experiment.number:
                    experiment.dependencies.add(dependency)
        experiment.paths.sort()
    return experiments


def check_layout(paths: list[str]) -> list[str]:
    errors: list[str] = []
    for path in paths:
        number = experiment_number(path)
        if number is None or number < STRUCTURED_START:
            continue
        match = STRUCTURED_RE.match(path)
        if not match or int(match.group(1)) != number:
            errors.append(
                f"GDT{number:03d} must live under experiments/yolo/gdt{number:03d}_<slug>/: {path}"
            )
    return errors


def human_size(size: int) -> str:
    value = float(size)
    for unit in ("B", "KiB", "MiB", "GiB"):
        if value < 1024 or unit == "GiB":
            return f"{value:.1f} {unit}" if unit != "B" else f"{int(value)} B"
        value /= 1024
    raise AssertionError("unreachable")


def md_link(path: str, label: str | None = None) -> str:
    if not path:
        return "—"
    target = "../" + path
    return f"[{label or Path(path).name}]({target})"


def render(experiments: dict[int, Experiment]) -> tuple[bytes, bytes]:
    fieldnames = [
        "experiment_id",
        "latest_date",
        "experiment_name",
        "status",
        "primary_report",
        "primary_report_exists",
        "layout",
        "file_count",
        "total_bytes",
        "ledger_entries",
        "manifest",
        "question",
        "claim_ceiling",
        "dependencies",
        "methods",
        "reports",
        "runners",
        "validators",
        "artifacts",
    ]
    rows: list[dict[str, str | int]] = []
    for number in sorted(experiments):
        experiment = experiments[number]
        classes = classify_paths(experiment.paths)
        latest = experiment.ledger_rows[-1] if experiment.ledger_rows else {}
        manifest = experiment.manifest
        manifest_reports = [
            binding.get("path", "")
            for binding in manifest.get("outputs", [])
            if "REPORT" in binding.get("role", "").upper()
        ]
        preferred_report = latest.get("primary_report", "")
        if not preferred_report and manifest_reports:
            preferred_report = manifest_reports[0]
        report, report_exists = resolve_report(preferred_report, classes["reports"])
        total_bytes = sum((ROOT / path).stat().st_size for path in experiment.paths)
        dependencies = set(experiment.dependencies)
        for dependency in manifest.get("dependencies", []):
            match = GDT_RE.search(dependency)
            if match:
                dependencies.add(int(match.group(1)))
        rows.append(
            {
                "experiment_id": f"GDT{number:03d}",
                "latest_date": latest.get("date", manifest.get("updated", "")),
                "experiment_name": latest.get(
                    "experiment", manifest.get("title", f"GDT{number:03d}")
                ),
                "status": latest.get("status", manifest.get("status", "UNREGISTERED")),
                "primary_report": report,
                "primary_report_exists": str(report_exists).lower(),
                "layout": describe_layout(number, experiment.paths),
                "file_count": len(experiment.paths),
                "total_bytes": total_bytes,
                "ledger_entries": len(experiment.ledger_rows),
                "manifest": experiment.manifest_path,
                "question": manifest.get("question", ""),
                "claim_ceiling": manifest.get("claim_ceiling", ""),
                "dependencies": ";".join(f"GDT{item:03d}" for item in sorted(dependencies)),
                "methods": ";".join(classes["methods"]),
                "reports": ";".join(classes["reports"]),
                "runners": ";".join(classes["runners"]),
                "validators": ";".join(classes["validators"]),
                "artifacts": ";".join(classes["artifacts"]),
            }
        )

    tsv = io.StringIO(newline="")
    writer = csv.DictWriter(tsv, fieldnames=fieldnames, delimiter="\t", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)

    tracked_files = sum(int(row["file_count"]) for row in rows)
    tracked_bytes = sum(int(row["total_bytes"]) for row in rows)
    structured = sum(row["layout"] == "STRUCTURED_YOLO" for row in rows)
    unregistered = sum(row["status"] == "UNREGISTERED" for row in rows)
    lines = [
        "# Experiment index",
        "",
        "Generated by `tools/build_experiment_index.py`; do not edit by hand.",
        "The authoritative scientific status remains",
        "[`semantic_assumptions/ACTIVE_EXPERIMENT_LEDGER.tsv`](semantic_assumptions/ACTIVE_EXPERIMENT_LEDGER.tsv).",
        "",
        "## Inventory",
        "",
        f"- Experiments indexed: **{len(rows)}**",
        f"- Experiment-associated tracked files: **{tracked_files:,}** ({human_size(tracked_bytes)})",
        f"- Structured GDT337+ experiments: **{structured}**",
        f"- IDs without a ledger entry: **{unregistered}**",
        f"- Full machine-readable paths, manifests, dependencies, questions, and claim ceilings: [`EXPERIMENT_INDEX.tsv`](EXPERIMENT_INDEX.tsv)",
        "  (`UNREGISTERED` means absent from the authoritative active ledger; it does not mean that files or branch-local results are absent.)",
        "",
        "GDT001–GDT336 are the byte-frozen legacy flat layout. Starting with",
        "GDT337, new work must use `experiments/yolo/gdtNNN_<slug>/`.",
        "",
        "## Experiments",
        "",
        "| ID | Latest ledger entry | Status | Primary report | Files | Size | Dependencies | Layout |",
        "|---|---|---|---|---:|---:|---:|---|",
    ]
    for row in reversed(rows):
        report = md_link(str(row["primary_report"]), "report") if row["primary_report_exists"] == "true" else "—"
        status = str(row["status"]).replace("|", "\\|")
        name = str(row["experiment_name"]).replace("|", "\\|")
        deps = 0 if not row["dependencies"] else len(str(row["dependencies"]).split(";"))
        lines.append(
            f"| {row['experiment_id']} | {name} | `{status}` | {report} | "
            f"{int(row['file_count']):,} | {human_size(int(row['total_bytes']))} | {deps} | {row['layout']} |"
        )
    lines.append("")
    return tsv.getvalue().encode(), ("\n".join(lines)).encode()


def write_or_check(path: Path, expected: bytes, check: bool) -> bool:
    if check:
        actual = path.read_bytes() if path.exists() else b""
        if actual != expected:
            print(f"STALE {path.relative_to(ROOT)}", file=sys.stderr)
            return False
        return True
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(expected)
    print(f"WROTE {path.relative_to(ROOT)} ({len(expected)} bytes)")
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="verify indexes and GDT337+ layout without writing")
    args = parser.parse_args()

    paths = git_paths()
    layout_errors = check_layout(paths)
    for error in layout_errors:
        print(f"LAYOUT_ERROR {error}", file=sys.stderr)
    experiments = build_experiments(paths, load_ledger())
    tsv, markdown = render(experiments)
    ok = write_or_check(TSV_OUT, tsv, args.check)
    ok = write_or_check(MD_OUT, markdown, args.check) and ok
    return 0 if ok and not layout_errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
