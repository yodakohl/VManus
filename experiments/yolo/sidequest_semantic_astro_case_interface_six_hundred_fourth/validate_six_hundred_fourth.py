#!/usr/bin/env python3
"""Validate the case-to-Astro workshop interface."""

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    plans = read("SIX_HUNDRED_FOURTH_SIX_CASE_CONDITION_PLANS.tsv")
    namespaces = read("SIX_HUNDRED_FOURTH_THIRTEEN_NAMESPACE_CASE_INTERFACE.tsv")
    loci = read("SIX_HUNDRED_FOURTH_142_LOCUS_CASE_INTERFACE.tsv")
    ledger = read("SIX_HUNDRED_FOURTH_776_GROUP_WORKSHOP_LEDGER.tsv")
    prose = [row for row in ledger if row["section"] == "PROSE_CASE"]
    astro = [row for row in ledger if row["section"] == "ASTRO_CONDITION_LABEL"]
    checks = {
        "six_case_plans": len(plans) == 6 and {row["case_id"] for row in plans} == {f"C{i}" for i in range(1, 7)},
        "thirteen_namespaces": len(namespaces) == 13 and len({row["canonical_namespace_id"] for row in namespaces}) == 13,
        "loci142": len(loci) == 142 and len({(row["page"], row["locus"]) for row in loci}) == 142,
        "prose381": len(prose) == 381,
        "astro395": len(astro) == 395,
        "unified776": len(ledger) == 776 and len({row["unified_id"] for row in ledger}) == 776,
        "all_cases_have_primary_namespace": all(row["primary_astro_namespace"] for row in plans),
        "local_labels_whole": all(row["semantic_label_de"] == "LOCAL_CELESTIAL_LABEL_MEMORIZED_AS_WHOLE" for row in loci),
        "no_orientation": all(row["orientation"] == "NONE" for row in loci),
        "no_cross_page_key": all(row["cross_page_key"] == "NONE" for row in loci),
        "no_written_pointer": all(row["cross_section_pointer"] == "NONE" for row in ledger),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SIX_HUNDRED_FOURTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
