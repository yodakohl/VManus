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
    groups = read("TWO_HUNDRED_SEVENTY_FIFTH_395_GROUP_READINGS.tsv")
    loci = read("TWO_HUNDRED_SEVENTY_FIFTH_142_LOCUS_READINGS.tsv")
    contracts = read("TWO_HUNDRED_SEVENTY_FIFTH_THREE_INSTRUMENT_CONTRACTS.tsv")
    checks = {
        "395_groups": len(groups) == 395,
        "serials_1_395": [int(r["group_serial"]) for r in groups] == list(range(1, 396)),
        "142_loci": len(loci) == 142,
        "page_groups": Counter(r["page"] for r in groups) == {"f67r2": 190, "f68r1": 65, "f69v": 140},
        "page_loci": Counter(r["page"] for r in loci) == {"f67r2": 74, "f68r1": 37, "f69v": 31},
        "locus_group_sum": sum(int(r["group_count"]) for r in loci) == 395,
        "three_contracts": len(contracts) == 3,
        "no_orientation": all(r["orientation_claim"] == "NONE" for r in groups + contracts),
        "no_start": all(r["start_claim"] == "NONE" for r in groups + contracts),
        "no_cross_page_key": all(r["cross_page_key"] == "NONE" for r in groups + contracts),
        "all_atoms_nonempty": all(r["component_or_copy_reading_de"].strip() for r in groups),
        "all_locus_readings_nonempty": all(r["continuous_default_reading_de"].strip() for r in loci),
        "sealed_pages_absent": all(r["page"] not in {"f84", "f84r"} for r in groups),
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    (OUT / "VALIDATION.json").write_text(json.dumps({"status": status, "checks": checks}, indent=2) + "\n", encoding="utf-8")
    if status != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
