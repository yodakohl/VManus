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
    decisions = read("FOUR_HUNDRED_SIXTY_SIXTH_65_ADDRESS_CORE_DECISIONS.tsv")
    atoms = read("FOUR_HUNDRED_SIXTY_SIXTH_EIGHT_ASTRO_ADDRESS_CORES.tsv")
    groups = read("FOUR_HUNDRED_SIXTY_SIXTH_395_ASTRO_GROUP_ADDRESS_CORES.tsv")
    loci = read("FOUR_HUNDRED_SIXTY_SIXTH_142_ASTRO_LOCUS_ADDRESS_CORES.tsv")
    ledger = read("FOUR_HUNDRED_SIXTY_SIXTH_776_GROUP_ADDRESS_CORE_LEDGER.tsv")
    remaining = read("FOUR_HUNDRED_SIXTY_SIXTH_12_REMAINING_WHOLE_NAMES.tsv")
    checks = {
        "decisions_65": len(decisions) == 65,
        "atoms_8": len(atoms) == 8,
        "groups_395": len(groups) == 395,
        "loci_142": len(loci) == 142,
        "ledger_776": len(ledger) == 776,
        "remaining_12": len(remaining) == 12,
        "new_status_65": sum(row["transfer_status"] == "ASTRO_ADDRESS_CORE_RESOLVED_SEQUENCE" for row in groups) == 65,
        "total_resolved_383": sum(row["transfer_status"] != "ASTRO_LOCAL_LABEL" for row in groups) == 383,
        "selected_was_candidate": all(row["selected_parse"] in row["parse_alternatives"].split(" || ") for row in decisions),
        "all_atoms_used": all(int(row["support_groups"]) > 0 for row in atoms),
        "group_order": [row["group_serial"] for row in groups] == [str(n) for n in range(1, 396)],
        "locus_membership_once": sorted((serial for row in loci for serial in row["group_serials"].split("|")), key=int) == [str(n) for n in range(1, 396)],
        "ledger_partition": [sum(row["domain"] == domain for row in ledger) for domain in ("PROSE", "ASTRO")] == [381, 395],
        "all_defaults": all(row["atomic_default_de"] for row in ledger),
        "no_cross_join": all(row["cross_instrument_join"] == "NONE" for row in groups + loci),
        "astro_pages": {row["page"] for row in groups} == {"f67r2", "f68r1", "f69v"},
        "sealed_absent": all("f84" not in (row["page"] + row["locus"]).lower() for row in groups),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FOUR_HUNDRED_SIXTY_SIXTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(result)


if __name__ == "__main__":
    main()
