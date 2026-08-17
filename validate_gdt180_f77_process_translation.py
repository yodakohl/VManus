#!/usr/bin/env python3
"""Independent retained-artifact validator for GDT180."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def sha(name: str) -> str:
    return hashlib.sha256((ROOT / name).read_bytes()).hexdigest()


def rows(name: str) -> list[dict[str, str]]:
    with (ROOT / name).open(encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    checks: list[str] = []
    result = json.loads((ROOT / "gdt180_result.json").read_text())
    bridge = json.loads((ROOT / "experiments/semantic_assumptions/results/f77r_quality_transition_bridge.json").read_text())
    steps = rows("gdt180_f77_process_steps.tsv")
    transitions = rows("gdt180_f77_transition_translation.tsv")
    predictions = rows("gdt180_predictions.tsv")
    counter = rows("gdt180_counterexamples.tsv")

    assert len(steps) == 6
    assert [row["provisional_quality_state"] for row in steps] == ["COLD", "DRY", "HOT", "HOT", "MOIST", "COLD"]
    checks.append("state_sequence")
    by_locus: dict[tuple[str, str], dict] = {(row["locus"], row["edition"]): row for row in bridge["target_rows"]}
    for row in steps:
        for edition in ("ZL3b", "IT2a", "RF1b"):
            original = by_locus[(row["locus"], edition)]
            assert row[f"{edition}_surface"] == original["surface"]
            assert row["local_state_bits"] == original["bits"]
        checks.append(f"source:{row['locus']}")

    assert len(transitions) == 5
    assert [row["provisional_transition_class"] for row in transitions] == ["EARTH", "FIRE", "NONE_HOT_HOLD", "AIR", "WATER"]
    assert [int(row["visible_emission"]) for row in transitions] == [1, 1, 0, 1, 1]
    assert sum(int(row["exact_relation_match"]) for row in transitions) == 5
    checks.append("transition_and_emission_sequence")
    assert len(predictions) == 4 and all(row["failure"] for row in predictions)
    assert len(counter) == 6
    checks.append("predictions_and_counterexamples")

    for name, digest in result["inputs"].items():
        assert sha(name) == digest
        checks.append(f"input:{name}")
    for name, digest in result["outputs"].items():
        assert sha(name) == digest
        checks.append(f"output:{name}")
    assert sha("run_gdt180_f77_process_translation.py") == result["implementation"]
    checks.append("implementation")
    assert not result["f84r_accessed"]
    assert not any("f84r." in (ROOT / name).read_text() for name in result["outputs"])
    checks.append("f84r_absent")

    validation = {
        "experiment": result["experiment"],
        "status": "PASS",
        "checks": checks,
        "checks_passed": len(checks),
        "result_sha256": sha("gdt180_result.json"),
    }
    (ROOT / "gdt180_validation.json").write_text(json.dumps(validation, sort_keys=True, indent=2) + "\n")
    print(f"PASS {len(checks)}/{len(checks)}")


if __name__ == "__main__":
    main()
