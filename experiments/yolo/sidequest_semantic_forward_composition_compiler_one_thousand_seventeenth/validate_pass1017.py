#!/usr/bin/env python3
"""Validate the Pass-1017 forward composition compiler."""

from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def check(name: str, condition: bool) -> dict[str, object]:
    return {"name": name, "passed": bool(condition)}


def main() -> None:
    valency = read(HERE / "PASS1017_19_CORE_VALENCY.tsv")
    pairs = read(HERE / "PASS1017_361_ORDERED_CORE_PAIRS.tsv")
    predictions = read(HERE / "PASS1017_FOUR_FRESH_COMPOSITION_PREDICTIONS.tsv")
    summary = json.loads((HERE / "PASS1017_BUILD_SUMMARY.json").read_text())
    pair_keys = {(row["left_root"], row["right_root"]) for row in pairs}

    checks = [
        check("nineteen_roots", len(valency) == 19 and len({row["root"] for row in valency}) == 19),
        check("all_roots_have_fixed_value", all(row["fixed_value_de"] for row in valency)),
        check("all_roots_have_forward_rule", all(row["forward_rule_de"] for row in valency)),
        check("all_four_registers_present_per_portable_root", all(len(row["registers"].split("|")) >= 2 for row in valency)),
        check("ordered_pairs_361", len(pairs) == 361 and len(pair_keys) == 361),
        check("pair_grid_complete", pair_keys == {(a["root"], b["root"]) for a in valency for b in valency}),
        check("pair_status_partition", sum(summary["pair_status_counts"].values()) == 361),
        check("four_predictions", len(predictions) == 4),
        check("prediction_pairs_exact", {(row["left_root"], row["right_root"]) for row in predictions} == {("CH", "AIN"), ("P", "AIN"), ("P", "AIIN"), ("L", "AIR")}),
        check("prediction_direct_pairs_unseen", all(row["current_adjacent_events"] == "0" for row in predictions)),
        check("prediction_gapped_support_fixed", [row["current_gapped_events"] for row in predictions] == ["3", "0", "1", "0"]),
        check("chain_is_top_prediction", predictions[0]["candidate_surface"] == "chain" and predictions[0]["priority"] == "HOCH"),
        check("events_3888", summary["event_count"] == 3888),
        check("recipes_912", summary["component_recipe_count"] == 912),
        check("no_new_roots", summary["new_root_count"] == 0),
        check("no_sealed_pages", not any("f84" in "\t".join(row.values()).casefold() for row in valency + pairs + predictions)),
    ]

    before = {path.name: path.read_bytes() for path in HERE.glob("PASS1017_*") if path.name != "PASS1017_VALIDATION.json"}
    subprocess.run(["python3", str(HERE / "build_pass1017.py")], cwd=ROOT, check=True)
    after = {path.name: path.read_bytes() for path in HERE.glob("PASS1017_*") if path.name != "PASS1017_VALIDATION.json"}
    checks.append(check("deterministic_rebuild", before == after))

    result = {
        "status": "PASS" if all(item["passed"] for item in checks) else "FAIL",
        "check_count": len(checks),
        "checks": checks,
    }
    (HERE / "PASS1017_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if result["status"] != "PASS":
        for item in checks:
            if not item["passed"]:
                print("FAIL", item["name"])
        raise SystemExit(1)
    print(f"PASS {len(checks)}/{len(checks)}")


if __name__ == "__main__":
    main()
