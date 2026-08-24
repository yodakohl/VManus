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
    namespaces = read("FIVE_HUNDRED_FORTY_THIRD_THIRTEEN_ASTRO_PURPOSE_NAMESPACES.tsv")
    loci = read("FIVE_HUNDRED_FORTY_THIRD_ONE_HUNDRED_FORTY_TWO_DUAL_ASTRO_LOCI.tsv")
    groups = read("FIVE_HUNDRED_FORTY_THIRD_THREE_HUNDRED_NINETY_FIVE_ASTRO_GROUP_BINDING.tsv")
    instruments = read("FIVE_HUNDRED_FORTY_THIRD_THREE_DUAL_ASTRO_INSTRUMENTS.tsv")
    totals = read("FIVE_HUNDRED_FORTY_THIRD_TEN_PAGE_PURPOSE_TOTALS.tsv")
    total = next(row for row in totals if row["scope"] == "TEN_PAGE_TOTAL")
    checks = {
        "namespaces13": len(namespaces) == 13 and len({row["namespace_id"] for row in namespaces}) == 13,
        "loci142": len(loci) == 142 and Counter(row["page"] for row in loci) == Counter({"f67r2": 74, "f68r1": 37, "f69v": 31}),
        "groups395": len(groups) == 395 and Counter(row["page"] for row in groups) == Counter({"f67r2": 190, "f68r1": 65, "f69v": 140}),
        "instruments3": len(instruments) == 3,
        "astro_cost19_14": (sum(int(row["medical_insertion_cost"]) for row in namespaces), sum(int(row["technical_insertion_cost"]) for row in namespaces)) == (19, 14),
        "astro_wins1_6_ties6": Counter(row["local_winner"] for row in namespaces) == Counter({"MEDICAL": 1, "TECHNICAL": 6, "TIE": 6}),
        "ten_page42_33": (total["medical_insertions"], total["technical_insertions"]) == ("42", "33"),
        "all_loci_expanded": all(row["medical_expansion_de"] and row["technical_expansion_de"] for row in loci),
        "no_orientation": all(row["orientation"] == "UNORDERED_OR_UNSELECTED" for row in loci) and all(row["orientation"] == "NONE_SELECTED" for row in groups),
        "no_crosspage_join": all(row["f68_f69_mapping"] == "NONE" for row in loci) and all(row["crosspage_join"] == "NONE" for row in groups),
        "no_prose_import": all(row["prose_card_import"] == "NONE" for row in [*loci, *groups]),
        "fixed_pages_only": {row["page"] for row in loci} == {"f67r2", "f68r1", "f69v"},
        "seal_absent": all(not row["page"].lower().startswith("f84") for row in [*loci, *groups]),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FIVE_HUNDRED_FORTY_THIRD_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
