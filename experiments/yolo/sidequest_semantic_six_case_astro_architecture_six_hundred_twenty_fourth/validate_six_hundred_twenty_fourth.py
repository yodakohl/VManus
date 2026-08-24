#!/usr/bin/env python3
"""Validate the corrected six-case plus optional-Astro architecture."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    cases = read("SIX_HUNDRED_TWENTY_FOURTH_6_CASE_ARCHITECTURE.tsv")
    namespaces = read("SIX_HUNDRED_TWENTY_FOURTH_13_ASTRO_NAMESPACE_INTERFACE.tsv")
    loci = read("SIX_HUNDRED_TWENTY_FOURTH_142_ASTRO_LOCUS_INTERFACE.tsv")
    groups = read("SIX_HUNDRED_TWENTY_FOURTH_395_ASTRO_GROUP_INTERFACE.tsv")
    ledger = read("SIX_HUNDRED_TWENTY_FOURTH_776_TEN_PAGE_LEDGER.tsv")
    prose = [row for row in ledger if row["section"] == "PROSE_CASE"]
    astro = [row for row in ledger if row["section"] == "ASTRO_OPTIONAL_LABEL"]
    page_counts = Counter(row["page"] for row in ledger)
    checks = {
        "six_cases": len(cases) == 6 and {row["case_id"] for row in cases} == {f"C{i}" for i in range(1, 7)},
        "five_complete_pairs": sum(row["complete_preparation_application_pair"] == "YES" for row in cases) == 5,
        "one_optional_appendix": sum(row["architecture_class"] == "OPTIONAL_TECHNICAL_APPENDIX" for row in cases) == 1,
        "c6_has_no_herbal_record": next(row for row in cases if row["case_id"] == "C6")["preparation_record"] == "NONE",
        "c6_not_bound_to_c5": next(row for row in cases if row["case_id"] == "C6")["dependency_status"] == "C5_PRODUCT_COMPATIBLE_BUT_NOT_EXPLICITLY_BOUND",
        "prose381": len(prose) == 381 and len({row["unified_id"] for row in prose}) == 381,
        "prose173_cards": len({row["local_identity"] for row in prose}) == 173,
        "astro395": len(astro) == 395 and len({row["unified_id"] for row in astro}) == 395,
        "unified776": len(ledger) == 776 and len({row["unified_id"] for row in ledger}) == 776,
        "ten_pages": set(page_counts) == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r", "f67r2", "f68r1", "f69v"},
        "thirteen_namespaces": len(namespaces) == 13 and len({row["canonical_namespace_id"] for row in namespaces}) == 13,
        "loci142": len(loci) == 142 and len({(row["page"], row["locus"]) for row in loci}) == 142,
        "group_namespace_inventory": {row["canonical_namespace_id"] for row in groups} == {row["canonical_namespace_id"] for row in namespaces},
        "all_astro_optional_in_cases": all(row["astro_required_for_case"] == "NO" for row in cases),
        "all_astro_optional_in_namespaces": all(row["required_for_case"] == "NO" for row in namespaces),
        "all_astro_optional_in_loci": all(row["required_for_case"] == "NO" for row in loci),
        "all_astro_optional_in_groups": all(row["required_for_case"] == "NO" for row in groups),
        "all_astro_optional_in_ledger": all(row["required_for_case"] == "NO" for row in astro),
        "labels_whole": all(row["label_reading"] == "WHOLE_LOCAL_LABEL__NO_WORD_DECOMPOSITION" for row in groups),
        "no_orientation": all(row["orientation_or_rotation"] == "NONE" for row in groups) and all(row["orientation"] == "NONE" for row in loci),
        "no_cross_page_key": all(row["f68_f69_key"] == "NONE" for row in groups) and all(row["cross_page_key"] == "NONE" for row in loci),
        "no_prose_pointer": all(row["cross_section_pointer"] == "NONE" for row in groups) and all(row["cross_page_key"] == "NONE" for row in ledger),
        "no_astro_dictionary_import": all(row["prose_dictionary_import"] == "NONE" for row in groups),
        "no_sealed_pages": not any(row["page"].startswith("f84") for row in ledger),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SIX_HUNDRED_TWENTY_FOURTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
