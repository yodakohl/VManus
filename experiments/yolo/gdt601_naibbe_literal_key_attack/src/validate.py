#!/usr/bin/env python3
"""Validate compact GDT601 artifacts without reopening mixed transcription."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
HERE = Path(__file__).resolve().parent.parent
OUT = HERE / "artifacts"


def sha256(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    result_path = OUT / "gdt601_result.json"
    examples_path = OUT / "gdt601_top_chance_readings.tsv"
    result = json.loads(result_path.read_text())
    checks = []

    def check(name, passed):
        checks.append({"check": name, "passed": bool(passed)})

    check("experiment id", result["experiment_id"] == "GDT601")
    check(
        "decision status",
        result["status"] == "LITERAL_NAIBBE_KEY_REJECTED_ON_F84_FREE_91_FOLIO_CORPUS",
    )
    check("91 f84-free physical folios", result["voynich_source"]["physical_folios"] == 91)
    check("180 allowed page surfaces", result["voynich_source"]["pages"] == 180)
    check("f84 gate", result["voynich_source"]["f84"] == "FORBIDDEN_AND_NOT_MATERIALIZED")
    check("two languages by two corpora", len(result["model_results"]) == 4)
    control = next(
        row
        for row in result["model_results"]
        if row["language"] == "latin" and row["corpus"] == "naibbe_latin_positive_control"
    )
    targets = [row for row in result["model_results"] if row["corpus"].startswith("voynich")]
    check("positive control separation", control["order_z"] >= 8.0)
    check("target non-separation", all(row["order_z"] <= 0.0 for row in targets))
    check(
        "positive control strict coverage",
        result["coverage"]["naibbe_latin_positive_control"]["parsed_event_fraction"] == 1.0,
    )
    target_fraction = result["coverage"]["voynich_f84_free_91_folios"]["parsed_event_fraction"]
    check("target designed-form coverage sanity", 0.75 <= target_fraction <= 0.85)
    with examples_path.open(newline="") as handle:
        examples = list(csv.DictReader(handle, delimiter="\t"))
    check("12 examples per target language", len(examples) == 24)
    check("example f84 exclusion", all("f84" not in row["page"].lower() for row in examples))

    validation = {
        "experiment_id": "GDT601",
        "status": "PASS" if all(item["passed"] for item in checks) else "FAIL",
        "checks": checks,
        "artifact_sha256": {
            "gdt601_result.json": sha256(result_path),
            "gdt601_top_chance_readings.tsv": sha256(examples_path),
        },
    }
    validation_path = OUT / "gdt601_validation.json"
    validation_path.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n")
    print(json.dumps(validation, indent=2, sort_keys=True))
    return 0 if validation["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
