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
    cards = read("FOUR_HUNDRED_SIXTY_EIGHTH_173_CARD_COMMON_ACTION_DICTIONARY.tsv")
    events = read("FOUR_HUNDRED_SIXTY_EIGHTH_381_PROSE_EVENT_COMMON_ACTIONS.tsv")
    statements = read("FOUR_HUNDRED_SIXTY_EIGHTH_116_PROSE_STATEMENT_COMMON_ACTIONS.tsv")
    components = read("FOUR_HUNDRED_SIXTY_EIGHTH_35_COMPONENT_COMMON_ACTION_MANUAL.tsv")
    astro = read("FOUR_HUNDRED_SIXTY_EIGHTH_395_ASTRO_GROUP_COMMON_ACTIONS.tsv")
    loci = read("FOUR_HUNDRED_SIXTY_EIGHTH_142_ASTRO_LOCUS_COMMON_ACTIONS.tsv")
    ledger = read("FOUR_HUNDRED_SIXTY_EIGHTH_776_GROUP_COMMON_ACTION_LEDGER.tsv")
    dictionary = read("FOUR_HUNDRED_SIXTY_EIGHTH_52_UNIT_COMMON_ACTION_DICTIONARY.tsv")
    revisions = read("FOUR_HUNDRED_SIXTY_EIGHTH_SEVEN_COMMON_ACTION_REVISIONS.tsv")
    atomic = " ".join(row["atomic_default_de"] for row in ledger)
    old = re.compile(r"abkuehlen|waermen|seihen|Auszug|abziehen|Durchlass|abfuehren")
    checks = {
        "cards_173": len(cards) == 173,
        "events_381": len(events) == 381,
        "statements_116": len(statements) == 116,
        "components_35": len(components) == 35,
        "astro_395": len(astro) == 395,
        "loci_142": len(loci) == 142,
        "ledger_776": len(ledger) == 776,
        "dictionary_52": len(dictionary) == 52,
        "revisions_7": len(revisions) == 7,
        "old_narrow_defaults_absent": old.search(atomic) is None,
        "all_defaults": all(row["atomic_default_de"] for row in ledger),
        "event_order": [row["event_id"] for row in events] == [f"E{n:03d}" for n in range(1, 382)],
        "astro_order": [row["group_serial"] for row in astro] == [str(n) for n in range(1, 396)],
        "statement_once": sorted((event for row in statements for event in row["event_ids"].split("|")), key=lambda x: int(x[1:])) == [f"E{n:03d}" for n in range(1, 382)],
        "locus_once": sorted((serial for row in loci for serial in row["group_serials"].split("|")), key=int) == [str(n) for n in range(1, 396)],
        "ledger_partition": [sum(row["domain"] == domain for row in ledger) for domain in ("PROSE", "ASTRO")] == [381, 395],
        "whole_name_preserved": sum(row["nomenclator_resolution"] == "MEMORIZED_WHOLE_NAME" for row in astro) == 1,
        "no_cross_join": all(row["cross_instrument_join"] == "NONE" for row in astro + loci),
        "fixed_pages": {row["page"] for row in ledger} == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r", "f67r2", "f68r1", "f69v"},
        "sealed_absent": all("f84" not in (row["page"] + row["locus"]).lower() for row in ledger),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FOUR_HUNDRED_SIXTY_EIGHTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(result)


if __name__ == "__main__":
    main()
