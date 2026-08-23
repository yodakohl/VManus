#!/usr/bin/env python3
"""Validate the separate Astro apprentice compiler."""

from __future__ import annotations

import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    primitives = rows("NINETY_FOURTH_8_ASTRO_APPRENTICE_PRIMITIVES.tsv")
    loci = rows("NINETY_FOURTH_142_LOCUS_WRITE_TRACE.tsv")
    groups = rows("NINETY_FOURTH_395_GROUP_COPY_TRACE.tsv")
    instruments = rows("NINETY_FOURTH_3_INSTRUMENT_ROUNDTRIP.tsv")
    used = {part for row in loci for part in row["apprentice_primitive_sequence"].split(">")}
    checks = {
        "primitives_8": len(primitives) == 8,
        "all_primitives_used": used == {row["primitive_id"] for row in primitives},
        "loci_142": len(loci) == 142,
        "groups_395": len(groups) == 395,
        "group_serial_complete": [int(row["group_serial"]) for row in groups] == list(range(1, 396)),
        "instrument_counts": [(row["unit_id"], int(row["locus_count"]), int(row["group_count"])) for row in instruments] == [("A1", 74, 190), ("A2", 37, 65), ("A3", 31, 140)],
        "namespaces_11": sum(int(row["namespace_count"]) for row in instruments) == 11,
        "no_orientation": all(row["orientation"] == "NONE" for row in loci + instruments),
        "no_crosspage_key": all(row["crosspage_key"] == "NONE" for row in loci + instruments),
        "no_prose_import": all(row["prose_import"] == "NONE" for row in instruments),
        "fixed_pages_only": set(row["page"] for row in groups) == {"f67r2", "f68r1", "f69v"},
        "sealed_absent": all("f84" not in "\t".join(row.values()).lower() for row in loci + groups),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
