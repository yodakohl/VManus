#!/usr/bin/env python3
"""Independent integrity/arithmetic validator for GDT110."""
from __future__ import annotations

import csv
import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
RESULT = ROOT / "gdt110_result.json"
VALIDATION = ROOT / "gdt110_validation.json"
JOIN = ROOT / "gdt002_exploratory_visual_formal_join.tsv"
INVENTORY = ROOT / "gdt110_contact_gap_hpr2_inventory.tsv"
EFFECTS = ROOT / "gdt110_layer_effects.tsv"
PREDICTIONS = ROOT / "gdt110_representation_predictions.tsv"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    result = json.loads(RESULT.read_text(encoding="utf-8")); checks = []
    def check(name: str, passed: bool, detail: object = "") -> None:
        checks.append({"check": name, "passed": bool(passed), "detail": detail})

    source = sorted((row["locus"], row["array_id"], row["visual_state"]) for row in read(JOIN) if row["channel"] == "CONTACT_GAP")
    inventory = read(INVENTORY)
    observed = sorted((row["locus"], row["array_id"], row["visual_state"]) for row in inventory)
    check("panel_exact", source == observed, len(observed))
    check("panel_count", len(inventory) == 27)
    check("state_counts", Counter(row["visual_state"] for row in inventory) == Counter({"CLEAR_GAP": 18, "CONTACT": 8, "UNCERTAIN": 1}))
    check("five_arrays", len({row["array_id"] for row in inventory}) == 5)
    check("three_folios", len({row["physical_folio"] for row in inventory}) == 3)
    check("f84_absent", not any(row["locus"].startswith("f84r") for row in inventory))
    check("roles_unassigned", all(row["semantic_role"] == "UNASSIGNED" for row in inventory))

    labels = np.array([1 if row["visual_state"] == "CONTACT" else 0 if row["visual_state"] == "CLEAR_GAP" else -1 for row in inventory])
    arrays = [row["array_id"] for row in inventory]
    mixed = [array for array in sorted(set(arrays)) if {labels[i] for i, name in enumerate(arrays) if name == array and labels[i] >= 0} == {0, 1}]
    choices = []
    for array in mixed:
        indexes = [i for i, name in enumerate(arrays) if name == array and labels[i] >= 0]
        positive = sum(labels[i] == 1 for i in indexes)
        choices.append(list(itertools.combinations(indexes, positive)))
    worlds = int(np.prod([len(choice) for choice in choices]))
    check("exact_worlds", worlds == 2520, worlds)

    effects = read(EFFECTS); by = {row["feature"]: row for row in effects}
    check("six_features", set(by) == {"DY", "RIGHT", "DY_OR_RIGHT", "B3", "WRAPPER", "FRAME"})
    for feature in by:
        values = np.array([int(row[feature.lower()]) for row in inventory])
        per = []
        for array in mixed:
            indexes = [i for i, name in enumerate(arrays) if name == array and labels[i] >= 0]
            positive = [i for i in indexes if labels[i] == 1]; negative = [i for i in indexes if labels[i] == 0]
            per.append(float(values[positive].mean() - values[negative].mean()))
        value = float(np.mean(per))
        check(f"effect:{feature}", abs(value - float(by[feature]["within_array_effect"])) < 1e-10, value)
    check("wrapper_top", effects[0]["feature"] == "WRAPPER")
    check("dy_right_unstable", float(by["DY_OR_RIGHT"]["min_leave_array_effect"]) < 0 < float(by["DY_OR_RIGHT"]["max_leave_array_effect"]))
    check("b3_negative_control_small", abs(float(by["B3"]["within_array_effect"])) < .1)

    predictions = read(PREDICTIONS)
    check("four_representations", len(predictions) == 4)
    check("prediction_arithmetic", all(abs(float(row["baseline_bits"]) - float(row["held_bits"]) - float(row["gain_bits"])) < 1e-9 for row in predictions))
    check("selector_arithmetic", all(abs(float(row["selector_paid_gain_bits"]) - (float(row["gain_bits"]) - 2)) < 1e-9 for row in predictions))
    check("edge_stripped_best", predictions[0]["representation"] == "EDGE_STRIPPED_CHAR3")
    check("best_all_folios_positive", int(predictions[0]["positive_gain_folios"]) == 3)
    check("best_max_p_nonconfirming", float(predictions[0]["max_four_representation_p"]) > .05)
    check("status_exact", result["status"] == "HPR2_DY_RIGHT_CONTACT_GAP_CHANNEL_NOT_TRANSFERABLE")

    for group in ("inputs", "outputs", "documents", "implementation"):
        for name, digest in result[group].items():
            path = ROOT / name
            check(f"hash:{name}", path.exists() and sha(path) == digest)
    check("f84_flags_false", all(value is False for value in result["f84r"].values()))
    check("report_ceiling", "No relation meaning" in (ROOT / "GDT110_HPR2_CONTACT_GAP_RELATION_CHANNEL_REPORT.md").read_text(encoding="utf-8"))

    passed = all(row["passed"] for row in checks)
    validation = {"schema": "GDT110_HPR2_CONTACT_GAP_RELATION_CHANNEL_VALIDATION_V1",
                  "status": "PASS" if passed else "FAIL", "checks_passed": sum(row["passed"] for row in checks),
                  "checks_total": len(checks), "result_sha256": sha(RESULT), "checks": checks}
    VALIDATION.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": validation["status"], "checks": f"{validation['checks_passed']}/{validation['checks_total']}"}, sort_keys=True))
    if not passed: raise SystemExit(1)


if __name__ == "__main__":
    main()
