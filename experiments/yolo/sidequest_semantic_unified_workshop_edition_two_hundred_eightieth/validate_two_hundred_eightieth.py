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
    dictionary = read("TWO_HUNDRED_EIGHTIETH_172_ENTRY_WORKSHOP_DICTIONARY.tsv")
    ledger = read("TWO_HUNDRED_EIGHTIETH_776_UNIFIED_INTERLINEAR.tsv")
    manual = read("TWO_HUNDRED_EIGHTIETH_TWELVE_STEP_MANUAL.tsv")
    kinds = Counter(r["entry_kind"] for r in dictionary)
    classes = Counter(r["semantic_class"] for r in ledger)
    checks = {
        "172_dictionary": len(dictionary) == 172,
        "dictionary_kinds": kinds == {"STEM_FAMILY": 36, "PROSE_WHOLE_SIGN": 23, "ASTRO_WHOLE_SIGN": 46, "LOCAL_COPY_KEY": 67},
        "orders_1_172": [int(r["dictionary_order"]) for r in dictionary] == list(range(1, 173)),
        "776_ledger": len(ledger) == 776,
        "indices_1_776": [int(r["unified_index"]) for r in ledger] == list(range(1, 777)),
        "381_prose_395_astro": Counter(r["register"] for r in ledger) == {"PROSE": 381, "ASTRO": 395},
        "coverage_618_79_79": classes == {"PORTABLE_COMPOSITION": 618, "LEARNED_WHOLE_SIGN": 79, "LOCAL_COPY_LABEL": 79},
        "all_readings_nonempty": all(r["portable_reading_de"].strip() and r["local_default_de"].strip() for r in ledger),
        "twelve_manual_steps": len(manual) == 12 and [int(r["step"]) for r in manual] == list(range(1, 13)),
        "ten_pages_only": {r["page"] for r in ledger} == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r", "f67r2", "f68r1", "f69v"},
        "sealed_pages_absent": all(r["page"] not in {"f84", "f84r"} for r in ledger),
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    (OUT / "VALIDATION.json").write_text(json.dumps({"status": status, "checks": checks}, indent=2) + "\n", encoding="utf-8")
    if status != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
