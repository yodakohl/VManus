#!/usr/bin/env python3
import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def rows(name):
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    cards = rows("HUNDRED_FORTY_FIFTH_173_LAYERED_DICTIONARY.tsv")
    prose = rows("HUNDRED_FORTY_FIFTH_381_LAYERED_PROSE.tsv")
    statements = rows("HUNDRED_FORTY_FIFTH_116_LAYERED_STATEMENTS.tsv")
    astro = rows("HUNDRED_FORTY_FIFTH_395_OWNER_LOCAL_ASTRO.tsv")
    unified = rows("HUNDRED_FORTY_FIFTH_776_LAYERED_LEDGER.tsv")
    jobs = rows("HUNDRED_FORTY_FIFTH_FOUR_LAYERED_JOBS.tsv")
    checks = {
        "cards_173": len(cards) == 173,
        "active_cards_41": sum(r["portable_scope"] == "ACTIVE_CROSS_RECORD" for r in cards) == 41,
        "prose_381": len(prose) == 381,
        "statements_116": len(statements) == 116,
        "astro_395": len(astro) == 395,
        "unified_776": len(unified) == 776,
        "jobs_4": len(jobs) == 4,
        "serials_unique": len({r["unified_serial"] for r in unified}) == 776,
        "source_groups_unique": len({r["source_group_id"] for r in unified}) == 776,
        "prose_layers_381": sum(r["meaning_provenance"] == "PROSE_CARD_PLUS_OWNER" for r in unified) == 381,
        "astro_layers_395": sum(r["meaning_provenance"] == "ASTRO_OWNER_LOCAL_MENU" for r in unified) == 395,
        "astro_has_no_prose_values": all(r["portable_card_value_de"] == "NO_PROSE_CARD_VALUE" for r in unified if r["meaning_provenance"] == "ASTRO_OWNER_LOCAL_MENU"),
        "prose_has_values": all(r["portable_card_value_de"] != "NO_PROSE_CARD_VALUE" for r in unified if r["meaning_provenance"] == "PROSE_CARD_PLUS_OWNER"),
        "no_crosspage_keys": all(r["crosspage_key"] == "NONE" for r in unified),
        "no_empty_cells": all(all(v for v in r.values()) for table in (cards, prose, statements, astro, unified, jobs) for r in table),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
