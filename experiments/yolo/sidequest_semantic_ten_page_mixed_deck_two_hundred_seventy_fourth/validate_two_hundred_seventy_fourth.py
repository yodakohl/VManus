#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

OUT = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    components = read("TWO_HUNDRED_SEVENTY_FOURTH_REVISED_40_COMPONENTS.tsv")
    astro = read("TWO_HUNDRED_SEVENTY_FOURTH_LAYERED_395_ASTRO_GROUPS.tsv")
    totals = read("TWO_HUNDRED_SEVENTY_FOURTH_776_COVERAGE_TOTALS.tsv")
    inventory = read("TWO_HUNDRED_SEVENTY_FOURTH_APPRENTICE_INVENTORY.tsv")
    counts = Counter(r["coverage_class_274"] for r in astro)
    total_map = {r["coverage_class"]: int(r["event_or_group_count"]) for r in totals if r["register"] == "TEN_PAGE_TOTAL"}
    revised = {r["component_id"]: r for r in components}
    checks = {
        "40_components": len(components) == 40,
        "seven_revised_components": sum(r["revision_274"] == "CROSS_REGISTER_CONSOLIDATED" for r in components) == 7,
        "portable_values": {k: revised[k]["short_value_de"] for k in ("OT", "AR", "AL", "OL", "OR", "Y", "AIR")} == {"OT": "FOLGEPOSTEN", "AR": "VON_QUELLE", "AL": "ZU_ZIEL", "OL": "WEITER_GLEICHER_LAUF", "OR": "BEDINGUNGSANSATZ", "Y": "DIES_AKTUELLER_POSTEN", "AIR": "LAUF_BAHN"},
        "395_astro": len(astro) == 395,
        "astro_split": counts == {"PORTABLE_COMPOSITION": 265, "LEARNED_WHOLE_SIGN": 51, "LOCAL_COPY_LABEL": 79},
        "three_class_total": sum(counts.values()) == 395,
        "unified_split": total_map == {"PORTABLE_COMPOSITION": 618, "LEARNED_WHOLE_SIGN": 79, "LOCAL_COPY_LABEL": 79},
        "unified_total_776": sum(total_map.values()) == 776,
        "five_inventory_rows": len(inventory) == 5,
        "memorized_109": next(r for r in inventory if r["inventory_layer"] == "TOTAL_MEMORIZED_ENTRIES")["entry_count"] == "109",
        "local_copy_67": next(r for r in inventory if r["inventory_layer"] == "ASTRO_LOCAL_COPY_LABELS")["entry_count"] == "67",
        "all_three_pages": {r["page"] for r in astro} == {"f67r2", "f68r1", "f69v"},
        "sealed_pages_absent": all(r["page"] not in {"f84", "f84r"} for r in astro),
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    (OUT / "VALIDATION.json").write_text(json.dumps({"status": status, "checks": checks}, indent=2) + "\n", encoding="utf-8")
    if status != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
