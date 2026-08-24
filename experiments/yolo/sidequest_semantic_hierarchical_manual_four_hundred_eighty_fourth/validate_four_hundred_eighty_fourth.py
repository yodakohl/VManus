#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    manual = read("FOUR_HUNDRED_EIGHTY_FOURTH_283_ITEM_HIERARCHICAL_MANUAL.tsv")
    ledger = read("FOUR_HUNDRED_EIGHTY_FOURTH_776_FORWARD_RECONSTRUCTION.tsv")
    layers = read("FOUR_HUNDRED_EIGHTY_FOURTH_MANUAL_LAYER_COUNTS.tsv")
    units = read("FOUR_HUNDRED_EIGHTY_FOURTH_14_HIERARCHICAL_UNIT_EDITIONS.tsv")
    counts = Counter(row["layer"] for row in manual)
    expected = {
        "L1_SHARED_COMPONENT": 35, "L2_OWNER_CLASS": 38,
        "L3_SHARED_SENTENCE_MOTIF": 9, "L4_BIO_FORM_CARD": 7,
        "L5_LEARNED_WHOLE_CARD": 6, "L6_LOCAL_STATEMENT_FORM": 65,
        "L7_ASTRO_READING_RULE": 1, "L8_RENDERER_HABIT": 9,
        "L9_SURFACE_EXEMPLAR": 113,
    }
    checks = {
        "manual_283": len(manual) == 283,
        "layer_counts_exact": counts == expected,
        "nine_layers": len(layers) == 9,
        "ledger_776": len(ledger) == 776,
        "writer_order_exact": [int(row["writer_order"]) for row in ledger] == list(range(1, 777)),
        "prose_381": sum(row["domain"] == "PROSE" for row in ledger) == 381,
        "astro_395": sum(row["domain"] == "ASTRO" for row in ledger) == 395,
        "surface_exact_663": sum(row["surface_exact_without_exemplar"] == "YES" for row in ledger) == 663,
        "surface_exemplar_113": sum(row["surface_exact_without_exemplar"] == "NO" for row in ledger) == 113,
        "observed_surface_complete": all(row["observed_surface"] for row in ledger),
        "readings_complete": all(row["concrete_reading_de"] for row in ledger),
        "unit_14": len(units) == 14,
        "unit_groups_776": sum(int(row["groups"]) for row in units) == 776,
        "fixed_pages_only": {row["page"] for row in ledger} == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r", "f67r2", "f68r1", "f69v"},
        "sealed_pages_absent": all(not row["page"].startswith("f84") for row in ledger),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FOUR_HUNDRED_EIGHTY_FOURTH_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(result["status"])
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
