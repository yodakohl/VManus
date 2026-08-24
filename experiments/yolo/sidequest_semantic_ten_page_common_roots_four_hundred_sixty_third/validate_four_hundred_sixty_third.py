#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    cards = read("FOUR_HUNDRED_SIXTY_THIRD_173_CARD_COMMON_ROOT_DICTIONARY.tsv")
    prose = read("FOUR_HUNDRED_SIXTY_THIRD_381_PROSE_EVENT_COMMON_ROOTS.tsv")
    statements = read("FOUR_HUNDRED_SIXTY_THIRD_116_PROSE_STATEMENT_DUAL_READINGS.tsv")
    astro = read("FOUR_HUNDRED_SIXTY_THIRD_395_ASTRO_GROUP_COMMON_ROOTS.tsv")
    loci = read("FOUR_HUNDRED_SIXTY_THIRD_142_ASTRO_LOCUS_COMMON_ROOTS.tsv")
    ledger = read("FOUR_HUNDRED_SIXTY_THIRD_776_GROUP_TEN_PAGE_LEDGER.tsv")
    units = read("FOUR_HUNDRED_SIXTY_THIRD_14_UNIT_SUMMARY.tsv")
    components = read("FOUR_HUNDRED_SIXTY_THIRD_35_COMPONENT_COMMON_ROOT_MANUAL.tsv")
    revisions = read("FOUR_HUNDRED_SIXTY_THIRD_FIVE_COMMON_ROOT_REVISIONS.tsv")
    atomic_text = " ".join(row["small_value_de"] for row in cards)
    narrow = re.compile(r"Wasser|Zutat|Gefäß|fuellen|gefuellt|Klarauszug", re.IGNORECASE)
    checks = {
        "cards_173": len(cards) == 173,
        "prose_381": len(prose) == 381,
        "statements_116": len(statements) == 116,
        "astro_395": len(astro) == 395,
        "loci_142": len(loci) == 142,
        "ledger_776": len(ledger) == 776,
        "units_14": len(units) == 14,
        "components_35": len(components) == 35,
        "revisions_5": len(revisions) == 5,
        "revised_types_21": sum(row["common_root_revision"] == "YES" for row in cards) == 21,
        "revised_prose_events_28": sum(row["common_root_revision"] == "YES" for row in prose) == 28,
        "revised_astro_groups_36": sum(row["common_root_revision"] == "YES" for row in astro) == 36,
        "atomic_narrow_words_absent": narrow.search(atomic_text) is None,
        "atomic_defaults_complete": all(row["atomic_default_de"] for row in ledger),
        "ledger_partition": [sum(row["domain"] == domain for row in ledger) for domain in ("PROSE", "ASTRO")] == [381, 395],
        "prose_event_order": [row["event_id"] for row in prose] == [f"E{n:03d}" for n in range(1, 382)],
        "astro_group_order": [row["group_serial"] for row in astro] == [str(n) for n in range(1, 396)],
        "statement_events_once": sorted((event for row in statements for event in row["event_ids"].split("|")), key=lambda item: int(item[1:])) == [f"E{n:03d}" for n in range(1, 382)],
        "locus_groups_once": sorted((serial for row in loci for serial in row["group_serials"].split("|")), key=int) == [str(n) for n in range(1, 396)],
        "astro_status_partition": [sum(row["transfer_status"] == status for row in astro) for status in ("EXACT_PROSE_SURFACE", "UNIQUE_COMPONENT_SEQUENCE", "AMBIGUOUS_COMPONENT_SEQUENCE", "ASTRO_LOCAL_LABEL")] == [89, 152, 41, 113],
        "no_cross_join": all(row["cross_instrument_join"] == "NONE" for row in astro + loci),
        "fixed_pages_10": {row["page"] for row in ledger} == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r", "f67r2", "f68r1", "f69v"},
        "sealed_absent": all("f84" not in (row["page"] + row["locus"]).lower() for row in ledger),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FOUR_HUNDRED_SIXTY_THIRD_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(result)


if __name__ == "__main__":
    main()
