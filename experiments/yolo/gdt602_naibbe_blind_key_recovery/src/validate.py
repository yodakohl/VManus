#!/usr/bin/env python3
"""Validate GDT602 key-recovery artifacts."""

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


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    result_path = OUT / "gdt602_result.json"
    key_path = OUT / "gdt602_recovered_key.tsv"
    result = json.loads(result_path.read_text())
    with key_path.open(newline="") as handle:
        key_rows = list(csv.DictReader(handle, delimiter="\t"))
    checks = []

    def check(name, passed):
        checks.append({"check": name, "passed": bool(passed)})

    check("experiment id", result["experiment_id"] == "GDT602")
    check(
        "conditional recovery status",
        result["status"] == "NAIBBE_KEY_RECOVERED_CONDITIONAL_ON_ORACLE_SEGMENTATION",
    )
    check("52,641 control characters", result["problem"]["characters"] == 52641)
    check("396 observed code types", result["problem"]["observed_state_specific_types"] == 396)
    check("three seeds", [row["seed"] for row in result["capacity_mdl_seeds"]] == [1, 2, 3])
    check(
        "every capacity seed above 99.9% character recovery",
        all(row["weighted_character_accuracy"] > 0.999 for row in result["capacity_mdl_seeds"]),
    )
    check(
        "every capacity seed above 98% type recovery",
        all(row["type_accuracy"] > 0.98 for row in result["capacity_mdl_seeds"]),
    )
    check(
        "seed score convergence",
        max(row["score_bits_per_event"] for row in result["capacity_mdl_seeds"])
        - min(row["score_bits_per_event"] for row in result["capacity_mdl_seeds"])
        < 1e-10,
    )
    check(
        "unconstrained mode collapse",
        result["unconstrained_ml"]["weighted_character_accuracy"] < 0.25
        and result["unconstrained_ml"]["score_bits_per_event"]
        > result["truth_key_score_bits_per_event"],
    )
    check(
        "capacity typicality near truth",
        all(
            abs(
                result["typicality"]["capacity_mdl"][f"order_{order}_bits_per_event"]
                - result["typicality"]["truth"][f"order_{order}_bits_per_event"]
            )
            < 0.02
            for order in (2, 3, 4)
        ),
    )
    check("key row count", len(key_rows) == 396)
    check("key character count", sum(int(row["events"]) for row in key_rows) == 52641)
    check("five wrong rare types", sum(row["correct"] == "0" for row in key_rows) == 5)
    check("no f84 input", "f84" not in json.dumps(result).lower())

    validation = {
        "experiment_id": "GDT602",
        "status": "PASS" if all(row["passed"] for row in checks) else "FAIL",
        "checks": checks,
        "artifact_sha256": {
            "gdt602_result.json": sha256(result_path),
            "gdt602_recovered_key.tsv": sha256(key_path),
        },
    }
    (OUT / "gdt602_validation.json").write_text(
        json.dumps(validation, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps(validation, indent=2, sort_keys=True))
    return 0 if validation["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
