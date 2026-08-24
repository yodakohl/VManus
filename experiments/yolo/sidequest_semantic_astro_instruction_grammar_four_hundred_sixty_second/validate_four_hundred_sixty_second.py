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
    loci = read("FOUR_HUNDRED_SIXTY_SECOND_142_LOCUS_INSTRUCTION_GRAMMAR.tsv")
    instruments = read("FOUR_HUNDRED_SIXTY_SECOND_THREE_CONTROLLED_INSTRUMENTS.tsv")
    pressure = read("FOUR_HUNDRED_SIXTY_SECOND_SIX_CROSS_REGISTER_WORD_PRESSURES.tsv")
    classes = ["OPERATIONAL_INSTRUCTION", "MIXED_LOCAL_NAME_AND_OPERATION", "PARAMETER_OR_ADDRESS", "MIXED_LOCAL_NAME_AND_PARAMETER", "LOCAL_NAME_ONLY"]
    checks = {
        "loci_142": len(loci) == 142,
        "instruments_3": len(instruments) == 3,
        "pressures_6": len(pressure) == 6,
        "class_partition": [sum(row["instruction_class"] == item for row in loci) for item in classes] == [35, 28, 15, 16, 48],
        "page_matrix": [[sum(row["page"] == page and row["instruction_class"] == item for row in loci) for item in classes] for page in ("f67r2", "f68r1", "f69v")] == [[15, 20, 6, 15, 18], [12, 4, 5, 0, 16], [8, 4, 4, 1, 14]],
        "operation_loci_63": sum(row["instruction_class"] in classes[:2] for row in loci) == 63,
        "parameter_loci_31": sum(row["instruction_class"] in classes[2:4] for row in loci) == 31,
        "local_loci_48": sum(row["instruction_class"] == "LOCAL_NAME_ONLY" for row in loci) == 48,
        "group_membership_395": sorted((serial for row in loci for serial in row["group_serials"].split("|")), key=int) == [str(n) for n in range(1, 396)],
        "controlled_readings": all(row["controlled_reading_de"] for row in loci),
        "no_orientation": all(row["orientation"] == "UNSPECIFIED" for row in loci + instruments),
        "no_cross_join": all(row["cross_instrument_join"] == "NONE" for row in loci + instruments),
        "fixed_pages": {row["page"] for row in loci} == {"f67r2", "f68r1", "f69v"},
        "sealed_absent": all("f84" not in (row["page"] + row["locus"]).lower() for row in loci),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FOUR_HUNDRED_SIXTY_SECOND_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(result)


if __name__ == "__main__":
    main()
