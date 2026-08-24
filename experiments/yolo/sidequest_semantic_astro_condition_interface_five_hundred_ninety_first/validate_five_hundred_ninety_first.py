#!/usr/bin/env python3
import csv
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name):
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    groups = read("FIVE_HUNDRED_NINETY_FIRST_395_GROUP_ASTRO_INTERFACE.tsv")
    loci = read("FIVE_HUNDRED_NINETY_FIRST_142_LOCUS_ASTRO_INTERFACE.tsv")
    namespaces = read("FIVE_HUNDRED_NINETY_FIRST_THIRTEEN_NAMESPACES.tsv")
    comparison = read("FIVE_HUNDRED_NINETY_FIRST_PURPOSE_COMPARISON.tsv")
    checks = {
        "groups395": len(groups) == 395 and [int(row["group_serial"]) for row in groups] == list(range(1, 396)),
        "opaque_ids_unique": len({row["opaque_local_id"] for row in groups}) == 395,
        "loci142": len(loci) == 142 and len({row["locus"] for row in loci}) == 142,
        "group_locus_reconciliation": sum(int(row["group_count"]) for row in loci) == 395,
        "namespaces13": len(namespaces) == 13 and len({row["canonical_namespace_id"] for row in namespaces}) == 13,
        "namespace_group_reconciliation": sum(int(row["groups"]) for row in namespaces) == 395,
        "namespace_locus_reconciliation": sum(int(row["loci"]) for row in namespaces) == 142,
        "page_groups": Counter(row["page"] for row in groups) == Counter({"f67r2": 190, "f68r1": 65, "f69v": 140}),
        "page_loci": Counter(row["page"] for row in loci) == Counter({"f67r2": 74, "f68r1": 37, "f69v": 31}),
        "selectable125": sum(row["interface_role"] == "SELECTABLE_CELESTIAL_SLOT" for row in loci) == 125,
        "all_group_meanings_present": all(row["possible_condition_use_de"] and row["memory_atlas_rival_de"] for row in groups),
        "no_prose_import": all(row["prose_dictionary_import"] == "NONE" for row in groups),
        "no_cross_pointer": all(row["cross_section_pointer"] == "NONE" for row in groups),
        "no_orientation": all(row["orientation_or_rotation"] == "NONE" for row in groups),
        "no_f68_f69_key": all(row["f68_f69_key"] == "NONE" for row in groups),
        "comparison8": len(comparison) == 8,
        "only_fixed_pages": set(row["page"] for row in groups) == {"f67r2", "f68r1", "f69v"},
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FIVE_HUNDRED_NINETY_FIRST_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
