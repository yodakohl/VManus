#!/usr/bin/env python3
"""Independent compact validation of GDT179 retained artifacts."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def read_tsv(name: str) -> list[dict[str, str]]:
    with (ROOT / name).open(encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha(name: str) -> str:
    return hashlib.sha256((ROOT / name).read_bytes()).hexdigest()


def main() -> None:
    checks: list[str] = []
    result = json.loads((ROOT / "gdt179_result.json").read_text())
    anchors = read_tsv("experiments/semantic_assumptions/results/translation_anchor_human_review_panel_v1.tsv")
    source_rows = {
        row["physical_locus"]: row
        for row in anchors
        if row["anchor_id"] == "F57_TWO_REGISTER_WHEEL"
    }
    inventory = read_tsv("gdt179_f57_inscription_inventory.tsv")
    decoder = read_tsv("gdt179_quality_decoder.tsv")
    r2 = read_tsv("gdt179_r2_partition.tsv")
    predictions = read_tsv("gdt179_predictions.tsv")
    counter = read_tsv("gdt179_counterexamples.tsv")

    assert len(inventory) == 13 and {row["locus"] for row in inventory} == {f"f57v.{i}" for i in range(1, 14)}
    checks.append("complete_13_locus_inventory")
    assert len(decoder) == 8 and sum(int(row["exact_internal_match"]) for row in decoder) == 8
    checks.append("eight_decoder_matches")

    expected = {
        ("N1", "NORTHEAST"): (1, 0, "HOT"),
        ("N1", "SOUTHEAST"): (0, 1, "MOIST"),
        ("N1", "SOUTHWEST"): (0, 0, "COLD"),
        ("N1", "NORTHWEST"): (1, 1, "DRY"),
        ("D1", "NORTHEAST"): (0, 0, "HOT"),
        ("D1", "SOUTHEAST"): (1, 1, "MOIST"),
        ("D1", "SOUTHWEST"): (1, 0, "COLD"),
        ("D1", "NORTHWEST"): (0, 1, "DRY"),
    }
    for row in decoder:
        key = (row["register"], row["position"])
        got = (int(row["selector_bit"]), int(row["terminal_y_bit"]), row["decoded_quality"])
        assert got == expected[key]
        assert row["ownership"] in {"PROXIMITY_ONLY", "BETWEEN_FIGURES_PROXIMITY_ONLY"}
        source = source_rows[row["locus"]]
        readings = [source["ZL3b_raw"], source["IT2a_raw"], source["RF1b_raw"]]
        assert readings == [row["ZL3b"], row["IT2a"], row["RF1b"]]
        selector = [value.startswith("ot") for value in readings] if row["register"] == "N1" else ["ok" in value for value in readings]
        terminal = [value.endswith("y") for value in readings]
        assert len(set(selector)) == len(set(terminal)) == 1
        assert int(selector[0]) == int(row["selector_bit"])
        assert int(terminal[0]) == int(row["terminal_y_bit"])
        checks.append(f"decoder:{row['locus']}")

    assert [row["r2_slot9_state"] for row in r2] == ["f", "f", "p", "p"]
    assert [int(row["hot_side"]) for row in r2] == [1, 1, 0, 0]
    assert all(row["alias_count"] == "3" for row in r2)
    checks.append("r2_partition_and_aliases")
    assert len(predictions) == 4 and all(row["falsifier"] for row in predictions)
    checks.append("predictions_have_falsifiers")
    assert len(counter) == 8 and any("f84r remains sealed" in row["finding"] for row in counter)
    checks.append("counterexamples_and_seal")

    for name, digest in result["input_hashes"].items():
        assert sha(name) == digest
        checks.append(f"input_hash:{name}")
    for name, digest in result["output_hashes"].items():
        assert sha(name) == digest
        checks.append(f"output_hash:{name}")
    assert sha("run_gdt179_f57_page_translation.py") == result["implementation_hash"]
    checks.append("implementation_hash")
    assert not result["f84r_accessed"]
    assert not any("f84r." in (ROOT / name).read_text() for name in result["output_hashes"])
    checks.append("f84r_absent")

    validation = {
        "experiment": result["experiment"],
        "status": "PASS",
        "checks_passed": len(checks),
        "checks": checks,
        "result_sha256": sha("gdt179_result.json"),
    }
    (ROOT / "gdt179_validation.json").write_text(json.dumps(validation, sort_keys=True, indent=2) + "\n")
    print(f"PASS {len(checks)}/{len(checks)}")


if __name__ == "__main__":
    main()
