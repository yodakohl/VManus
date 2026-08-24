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
    astro = read("FOUR_HUNDRED_SEVENTY_SECOND_395_ASTRO_GROUP_CONTEXT_READINGS.tsv")
    loci = read("FOUR_HUNDRED_SEVENTY_SECOND_142_ASTRO_LOCUS_CONTEXT_READINGS.tsv")
    units = read("FOUR_HUNDRED_SEVENTY_SECOND_14_CONTINUOUS_UNIT_EDITIONS.tsv")
    collisions = read("FOUR_HUNDRED_SEVENTY_SECOND_35_COMPONENT_CONTENT_COLLISION_AUDIT.tsv")
    checks = {
        "astro_395": len(astro) == 395,
        "loci_142": len(loci) == 142,
        "units_14": len(units) == 14,
        "components_35": len(collisions) == 35,
        "unit_group_total_776": sum(int(row["groups"]) for row in units) == 776,
        "unit_partition": [sum(row["domain"] == domain for row in units) for domain in ("HERBAL", "BIOLOGICAL", "ASTRO")] == [5, 6, 3],
        "all_unit_readings": all(row["atomic_continuous_reading_de"] and row["context_continuous_reading_de"] for row in units),
        "all_astro_contexts": all(row["celestial_context_reading_de"] for row in astro),
        "locus_once": sorted((serial for row in loci for serial in row["group_serials"].split("|")), key=int) == [str(n) for n in range(1, 396)],
        "no_genuine_collisions": all(row["genuine_content_collision"] == "NO" for row in collisions),
        "no_cross_join": all(row["cross_instrument_join"] == "NONE" for row in loci),
        "fixed_pages": {row["page"] for row in units} == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r", "f67r2", "f68r1", "f69v"},
        "sealed_absent": all("f84" not in row["page"].lower() for row in units),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FOUR_HUNDRED_SEVENTY_SECOND_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(result)


if __name__ == "__main__":
    main()
