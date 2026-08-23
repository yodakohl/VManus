#!/usr/bin/env python3
"""Validate the separate Astro address manuals."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


OUT = Path(__file__).resolve().parent
ALLOWED = {"f67r2", "f68r1", "f69v"}


def read_tsv(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    groups = read_tsv("SIXTY_EIGHTH_395_ASTRO_GROUP_ADDRESS_LEDGER.tsv")
    loci = read_tsv("SIXTY_EIGHTH_142_ASTRO_LOCUS_MANUAL.tsv")
    instruments = read_tsv("SIXTY_EIGHTH_3_ASTRO_INSTRUMENT_CARDS.tsv")
    namespaces = read_tsv("SIXTY_EIGHTH_13_LOCAL_NAMESPACES.tsv")
    examples = read_tsv("SIXTY_EIGHTH_12_EXAMPLE_LOOKUPS.tsv")
    checks = {
        "three_pages": {row["page"] for row in groups} == ALLOWED,
        "395_groups": len(groups) == 395 and len({row["group_serial"] for row in groups}) == 395,
        "group_page_counts": Counter(row["page"] for row in groups) == Counter({"f67r2": 190, "f68r1": 65, "f69v": 140}),
        "142_loci": len(loci) == 142 and len({(row["page"], row["locus"]) for row in loci}) == 142,
        "locus_group_counts_reconcile": sum(int(row["group_count"]) for row in loci) == 395,
        "three_instruments": len(instruments) == 3 and {row["diagram_id"] for row in instruments} == {"A1", "A2", "A3"},
        "thirteen_namespaces": len(namespaces) == 13,
        "twelve_examples": len(examples) == 12,
        "no_orientation": all(row["orientation"] == "NONE" for row in groups + loci + instruments),
        "no_crosspage_key": all(row["crosspage_key"] == "NONE" for row in groups + loci) and all(row["crosspage_mapping"] == "NONE" for row in instruments),
        "no_prose_import": all(row["prose_grammar_import"] == "NONE" for row in groups) and all(row["prose_card_import"] == "NONE" for row in instruments),
        "sealed_pages_absent": all("f84" not in "\t".join(row.values()).lower() for row in groups + loci + instruments + namespaces + examples),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
