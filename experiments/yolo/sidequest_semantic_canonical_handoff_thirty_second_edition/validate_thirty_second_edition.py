#!/usr/bin/env python3
from pathlib import Path
import csv
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def read(name):
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


layers = read("THIRTY_SECOND_ACTIVE_LAYER_MAP.tsv")
hashes_match = all(
    hashlib.sha256((ROOT / row["path"]).read_bytes()).hexdigest() == row["sha256"]
    for row in layers
)
checks = {
    "twelve_layers": len(layers) == 12,
    "layer_names_unique": len({row["layer"] for row in layers}) == 12,
    "layer_hashes_match": hashes_match,
    "surface_dictionary_487": next(int(row["data_rows"]) for row in layers if row["layer"] == "surface_dictionary") == 487,
    "event_ledger_776": next(int(row["data_rows"]) for row in layers if row["layer"] == "event_ledger") == 776,
    "reading_units_258": next(int(row["data_rows"]) for row in layers if row["layer"] == "reading_units") == 258,
    "owner_statements_116": next(int(row["data_rows"]) for row in layers if row["layer"] == "owner_statements") == 116,
    "component_deck_56": next(int(row["data_rows"]) for row in layers if row["layer"] == "component_deck") == 56,
    "source_clauses_254": next(int(row["data_rows"]) for row in layers if row["layer"] == "source_clauses") == 254,
    "balanced_records_11": next(int(row["data_rows"]) for row in layers if row["layer"] == "balanced_records") == 11,
    "event_idioms_17": next(int(row["data_rows"]) for row in layers if row["layer"] == "event_idioms") == 17,
    "balanced_dossiers_4": next(int(row["data_rows"]) for row in layers if row["layer"] == "balanced_dossiers") == 4,
    "working_theory": (HERE / "THIRTY_SECOND_CANONICAL_WORKING_THEORY.md").exists(),
    "quick_reference": (HERE / "THIRTY_SECOND_QUICK_REFERENCE.md").exists(),
    "report": (HERE / "THIRTY_SECOND_EDITION_REPORT.md").exists(),
}
sealed = "f" + "84"
checks["sealed_absent"] = all(
    sealed not in path.read_text(encoding="utf-8").lower()
    for path in HERE.iterdir()
    if path.is_file()
)
result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
(HERE / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, ensure_ascii=False, indent=2))
if result["status"] != "PASS":
    raise SystemExit(1)
