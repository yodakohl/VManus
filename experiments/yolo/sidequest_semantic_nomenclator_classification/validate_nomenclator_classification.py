#!/usr/bin/env python3
from pathlib import Path
import csv
import json

HERE = Path(__file__).resolve().parent

def read(name):
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))

rows = read("CLASSIFIED_487_SURFACES.tsv")
burden = read("LEARNING_BURDEN.tsv")
deck = read("NOMENCLATOR_DECK.tsv")
checks = {
    "surface_count_487": len(rows) == 487,
    "unique_surface_ids": len({r["surface_id"] for r in rows}) == 487,
    "unique_visible_surfaces": len({r["visible_surface"] for r in rows}) == 487,
    "visible_groups_776": sum(int(r["prose_occurrences"]) + int(r["astro_occurrences"]) for r in rows) == 776,
    "prose_groups_381": sum(int(r["prose_occurrences"]) for r in rows) == 381,
    "astro_groups_395": sum(int(r["astro_occurrences"]) for r in rows) == 395,
    "burden_reconciles_types": sum(int(r["surface_types"]) for r in burden) == 487,
    "burden_reconciles_groups": sum(int(r["visible_groups"]) for r in burden) == 776,
    "deck_is_subset": {r["visible_surface"] for r in deck} <= {r["visible_surface"] for r in rows},
    "no_empty_classification": all(r["classification"] and r["apprentice_action_de"] for r in rows),
    "report_present": (HERE / "NOMENCLATOR_CLASSIFICATION_REPORT.md").stat().st_size > 2000,
}
sealed = "f" + "84"
checks["sealed_token_absent"] = all(sealed not in p.read_text(encoding="utf-8").lower() for p in HERE.iterdir() if p.is_file())
result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
(HERE / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, ensure_ascii=False, indent=2))
if result["status"] != "PASS":
    raise SystemExit(1)
