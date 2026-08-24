#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    groups = read("FOUR_HUNDRED_SIXTY_FIRST_395_ASTRO_GROUP_TRANSFER.tsv")
    loci = read("FOUR_HUNDRED_SIXTY_FIRST_142_ASTRO_LOCUS_READINGS.tsv")
    instruments = read("FOUR_HUNDRED_SIXTY_FIRST_THREE_INSTRUMENT_READINGS.tsv")
    atoms = read("FOUR_HUNDRED_SIXTY_FIRST_COMPONENT_SURFACE_LEXICON.tsv")
    status = ["EXACT_PROSE_SURFACE", "UNIQUE_COMPONENT_SEQUENCE", "AMBIGUOUS_COMPONENT_SEQUENCE", "ASTRO_LOCAL_LABEL"]
    checks = {
        "groups_395": len(groups) == 395,
        "group_serials": [row["group_serial"] for row in groups] == [str(n) for n in range(1, 396)],
        "loci_142": len(loci) == 142,
        "instruments_3": len(instruments) == 3,
        "status_partition": [sum(row["transfer_status"] == item for row in groups) for item in status] == [89, 152, 41, 113],
        "transferred_241": sum(row["transfer_status"] in status[:2] for row in groups) == 241,
        "page_matrix": [[sum(row["page"] == page and row["transfer_status"] == item for row in groups) for item in status] for page in ("f67r2", "f68r1", "f69v")] == [[39, 74, 12, 65], [8, 29, 12, 16], [42, 49, 17, 32]],
        "page_group_counts": [sum(row["page"] == page for row in groups) for page in ("f67r2", "f68r1", "f69v")] == [190, 65, 140],
        "page_locus_counts": [sum(row["page"] == page for row in loci) for page in ("f67r2", "f68r1", "f69v")] == [74, 37, 31],
        "locus_groups_once": sorted((serial for row in loci for serial in row["group_serials"].split("|")), key=int) == [str(n) for n in range(1, 396)],
        "exact_ids_present": all(row["exact_prose_joint_tuple_id"] != "NONE" for row in groups if row["transfer_status"] == "EXACT_PROSE_SURFACE"),
        "unique_parses_present": all(row["selected_component_parse"] != "NONE" for row in groups if row["transfer_status"] == "UNIQUE_COMPONENT_SEQUENCE"),
        "ambiguous_has_alternatives": all(" || " in row["parse_alternatives"] for row in groups if row["transfer_status"] == "AMBIGUOUS_COMPONENT_SEQUENCE"),
        "atoms_nonempty": len(atoms) > 35 and all(row["components"] and row["values_de"] for row in atoms),
        "owners_preserved": all(row["owner_and_namespace_preserved"] == "YES" and row["visible_owner"] and row["local_namespace"] for row in groups),
        "no_cross_join": all(row["cross_instrument_join"] == "NONE" for row in groups + loci + instruments),
        "fixed_pages": {row["page"] for row in groups} == {"f67r2", "f68r1", "f69v"},
        "sealed_absent": all("f84" not in (row["page"] + row["locus"]).lower() for row in groups),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FOUR_HUNDRED_SIXTY_FIRST_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(result)


if __name__ == "__main__":
    main()
