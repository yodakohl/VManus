#!/usr/bin/env python3
"""Independent integrity checks for the V66 R2 generated tables."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent


def rows(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    groups = rows("V66_R2_395_GROUP_ASTRO_INTERLINEAR.tsv")
    loci = rows("V66_R2_142_LOCUS_EDITIONS.tsv")
    diagrams = rows("V66_R2_THREE_DIAGRAM_EDITIONS.tsv")
    sources = rows("V66_R2_HISTORICAL_SOURCES.tsv")
    expected_pages = {"f67r2", "f68r1", "f69v"}
    group_pages = Counter(row["page"] for row in groups)
    locus_pages = Counter(row["page"] for row in loci)
    f69_rules = [row for row in loci if row["page"] == "f69v" and int(row["locus_number"]) >= 4]
    repeated_okeod = [
        row["complete_local_exemplar_German"]
        for row in f69_rules
        if row["surface_sequence_ZL3b"] == "okeod"
    ]
    checks = {
        "groups_395": len(groups) == 395,
        "loci_142": len(loci) == 142,
        "diagrams_3": len(diagrams) == 3,
        "sources_8": len(sources) == 8,
        "pages_exact": set(group_pages) == expected_pages == set(locus_pages),
        "group_partition": group_pages == {"f67r2": 190, "f68r1": 65, "f69v": 140},
        "locus_partition": locus_pages == {"f67r2": 74, "f68r1": 37, "f69v": 31},
        "serials_complete": [int(row["group_serial"]) for row in groups] == list(range(1, 396)),
        "event_serials_strict": [int(row["source_event_serial"]) for row in groups] == sorted(int(row["source_event_serial"]) for row in groups),
        "all_defaults_present": all(row["default_content_German"].strip() for row in groups),
        "all_defaults_local_not_gloss": all("KEINE KARTENGLOSSE" in row["default_content_German"] and row["content_status"] == "LOCAL_EXEMPLAR_SEGMENT_NOT_PORTABLE_CARD_VALUE" for row in groups),
        "no_forbidden_page": not any(row["page"].startswith("f84") for row in groups + loci + diagrams),
        "f68_stations_28": sum(row["structural_role"] == "SPATIAL_LUNAR_MANSION_LOCAL_EXEMPLAR" for row in loci) == 28,
        "f69_rules_28": len(f69_rules) == 28,
        "okeod_three_and_consistent": len(repeated_okeod) == 3 and len(set(repeated_okeod)) == 1,
        "mapping_none": all(row["f68_f69_mapping"] == "NONE" for row in groups + loci),
        "rotation_uncertainty": all("UNPROVEN" in row["rotation_start_status"] for row in groups + loci),
        "external_labels_flagged": all(row["external_label_status"] != "NONE" for row in groups if row["locus_role"] in {"ZODIAC_BODY_SECTOR_LOCAL_EXEMPLAR", "SEVEN_PLANET_LOCAL_EXEMPLAR", "TWELVE_HOUSE_CONTROL_LOCAL_EXEMPLAR", "SPATIAL_LUNAR_MANSION_LOCAL_EXEMPLAR"}),
    }
    result = {
        "validator": "V66_R2_VALIDATE_HISTORICAL_ASTRO_EDITION.py",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks_passed": sum(checks.values()),
        "checks_total": len(checks),
        "checks": checks,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
