#!/usr/bin/env python3
import csv
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent


def rows(name):
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    atoms = rows("HUNDRED_TWENTY_FIRST_44_ATOM_LEXICON.tsv")
    cards = rows("HUNDRED_TWENTY_FIRST_173_TEACHING_DICTIONARY.tsv")
    surfaces = rows("HUNDRED_TWENTY_FIRST_230_SURFACE_INDEX.tsv")
    clauses = rows("HUNDRED_TWENTY_FIRST_254_OWNER_CLAUSES.tsv")
    events = rows("HUNDRED_TWENTY_FIRST_381_EVENT_INTERLINEAR.tsv")
    statements = rows("HUNDRED_TWENTY_FIRST_116_CURRENT_STATEMENTS.tsv")
    astro = rows("HUNDRED_TWENTY_FIRST_395_ASTRO_GROUPS.tsv")
    unified = rows("HUNDRED_TWENTY_FIRST_776_UNIFIED_LEDGER.tsv")
    shared = rows("HUNDRED_TWENTY_FIRST_17_SHARED_CARDS.tsv")
    hands = rows("HUNDRED_TWENTY_FIRST_FOUR_HAND_MANUAL.tsv")
    checks = {
        "atoms_44": len(atoms) == 44,
        "cards_173": len(cards) == 173,
        "surfaces_230": len(surfaces) == 230,
        "clauses_254": len(clauses) == 254,
        "events_381": len(events) == 381,
        "statements_116": len(statements) == 116,
        "astro_395": len(astro) == 395,
        "unified_776": len(unified) == 776,
        "shared_17": len(shared) == 17,
        "hands_4": len(hands) == 4,
        "event_ids_unique": len({r["event_serial"] for r in events}) == 381,
        "statement_ids_unique": len({r["statement_id"] for r in statements}) == 116,
        "cards_resolve": {r["master_card_id"] for r in events} <= {r["master_card_id"] for r in cards},
        "all_owner_resolved": all(r["final_owner_status"] != "OWNER_UNRESOLVED" for r in clauses),
        "renderer_306_75": sum(r["revised_renderer_status"] != "COPY_MASTER_EXEMPLAR_OVERRIDE" for r in events) == 306 and sum(r["revised_renderer_status"] == "COPY_MASTER_EXEMPLAR_OVERRIDE" for r in events) == 75,
        "formula_tags_present": any(r["formula_tags"] != "NONE" for r in statements),
        "sealed_absent": all("f84" not in "\t".join(r.values()).lower() for r in unified),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
