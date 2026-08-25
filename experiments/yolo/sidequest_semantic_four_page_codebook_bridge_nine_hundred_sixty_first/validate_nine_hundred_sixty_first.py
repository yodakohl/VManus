#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


OUT = Path(__file__).resolve().parent


def read_tsv(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    roots = read_tsv("PASS961_56_ROOT_OLD10_NEW4_BRIDGE.tsv")
    formulas = read_tsv("PASS961_66_FORMULA_OLD10_NEW4_BRIDGE.tsv")
    layers = read_tsv("PASS961_LAYER_BRIDGE_SUMMARY.tsv")
    formula_status = Counter(row["bridge_status"] for row in formulas)
    root_status = Counter(row["bridge_status"] for row in roots)
    checks = {
        "roots_56": len(roots) == 56,
        "root_bridge_48": root_status["BRIDGES_BOTH"] == 48,
        "formulas_66": len(formulas) == 66,
        "formula_bridge_61": formula_status["BRIDGES_BOTH"] == 61,
        "no_new_only_formula": formula_status["NEW4_ONLY"] == 0,
        "old_only_formula_5": formula_status["OLD10_ONLY"] == 5,
        "new_formula_events_274": sum(int(row["new4_events"]) for row in formulas) == 274,
        "all_new_formula_events_bridge": sum(int(row["new4_events"]) for row in formulas if row["bridge_status"] == "BRIDGES_BOTH") == 274,
        "layers_3": len(layers) == 3,
        "productive_bridge_200_of_345": any(row["layer"] == "PRODUCTIVE_ABBREVIATION_COMPOSITION" and row["new4_events"] == "345" and row["new4_events_with_old10_recipe"] == "200" for row in layers),
        "no_sealed_pages": not any("f84" in str(row).lower() for row in roots + formulas + layers),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "PASS961_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
