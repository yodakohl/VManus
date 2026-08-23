#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from pathlib import Path

OUT = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def hashes() -> dict[str, str]:
    names = ["TWO_HUNDRED_SIXTEENTH_776_LAYERED_LEDGER.tsv", "TWO_HUNDRED_SIXTEENTH_14_UNIT_LAYER_SUMMARY.tsv", "TWO_HUNDRED_SIXTEENTH_LAYER_DICTIONARY.tsv", "BUILD_SUMMARY.json"]
    return {name: hashlib.sha256((OUT / name).read_bytes()).hexdigest() for name in names}


def main() -> None:
    ledger = read("TWO_HUNDRED_SIXTEENTH_776_LAYERED_LEDGER.tsv")
    units = read("TWO_HUNDRED_SIXTEENTH_14_UNIT_LAYER_SUMMARY.tsv")
    layers = read("TWO_HUNDRED_SIXTEENTH_LAYER_DICTIONARY.tsv")
    summary = json.loads((OUT / "BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    expected = {
        "COMMON_PORTABLE_CARD": 116,
        "LOCAL_CARD_WITH_COMMON_AXIS": 203,
        "PROSE_COMPONENT_CARD": 37,
        "LOCAL_WHOLE_CARD": 24,
        "LOCAL_PRODUCTIVE_CARD_CORE": 1,
        "COMMON_PORTABLE_SURFACE": 66,
        "ASTRO_LOCAL_LABEL_WITH_PROSE_HOMOGRAPH": 23,
        "ASTRO_LOCAL_EXEMPLAR": 306,
    }
    checks = {
        "776_groups": len(ledger) == 776 and [int(row["unified_serial"]) for row in ledger] == list(range(1, 777)),
        "381_plus_395": summary["prose_events"] == 381 and summary["astro_groups"] == 395,
        "14_units": len(units) == 14 and {row["unit_id"] for row in units} == {"H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6", "A1", "A2", "A3"},
        "eight_layers": len(layers) == 8,
        "exact_layer_counts": summary["layer_counts"] == expected,
        "182_common_portable": summary["common_portable_total"] == 182,
        "every_group_one_layer": all(row["primary_layer"] in expected for row in ledger),
        "common_values_nonempty": all(row["portable_core_value_de"] != "NONE" for row in ledger if row["primary_layer"] in {"COMMON_PORTABLE_CARD", "COMMON_PORTABLE_SURFACE"}),
        "local_expansions_nonempty": all(row["local_expansion_de"] for row in ledger),
        "fixed_pages_only": {row["page"] for row in ledger} == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r", "f67r2", "f68r1", "f69v"},
        "sealed_not_accessed": summary["sealed_pages_accessed"] is False,
        "sealed_absent": not any("f84" in value.lower() for rows in (ledger, units, layers) for row in rows for value in row.values()),
    }
    first = hashes()
    subprocess.run(["python3", str(OUT / "build_two_hundred_sixteenth.py")], check=True)
    second = hashes()
    checks["deterministic_rebuild"] = first == second
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "summary": summary, "artifact_sha256": second}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
