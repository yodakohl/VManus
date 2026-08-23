#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def rows(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    cards = rows("TWO_HUNDRED_FIFTY_SEVENTH_173_CARD_DICTIONARY.tsv")
    events = rows("TWO_HUNDRED_FIFTY_SEVENTH_381_PROSE_EVENTS.tsv")
    statements = rows("TWO_HUNDRED_FIFTY_SEVENTH_116_STATEMENTS.tsv")
    revisions = rows("TWO_HUNDRED_FIFTY_SEVENTH_FIVE_REVISIONS.tsv")
    event_ids = {r["master_card_id"]: r for r in cards}
    expected = {"MC115", "MC061", "MC124", "MC049", "MC068"}
    checks = {
        "173_cards": len(cards) == 173 and len({r["master_card_id"] for r in cards}) == 173,
        "381_events": len(events) == 381 and len({r["event_id"] for r in events}) == 381,
        "116_statements": len(statements) == 116 and len({r["statement_id"] for r in statements}) == 116,
        "five_revisions": len(revisions) == 5 and {r["master_card_id"] for r in revisions} == expected,
        "five_revised_events": sum(r["revision_257"] == "REVISED" for r in events) == 5,
        "five_rewritten_statements": sum(r["revision_257"] == "REWRITTEN" for r in statements) == 5,
        "event_dictionary_identity": all(r["portable_core_de"] == event_ids[r["master_card_id"]]["portable_core_de"] for r in events),
        "triple_exact": event_ids["MC115"]["portable_core_de"] == "danach mit diesem Posten weiter",
        "four_blocker_layers": sum(r["dictionary_layer"] == "LEXICAL_BLOCKER_WHOLE_SIGN" for r in cards) == 4,
        "no_empty_readings": all(r["complete_local_translation_de"].strip() for r in statements),
        "fixed_pages_only": {r["page"] for r in events} <= {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
        "sealed_pages_absent": all("f84" not in "\t".join(r.values()).lower() for r in events),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "VALIDATION.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        print(json.dumps(result, indent=2, ensure_ascii=False))
        raise SystemExit(1)
    print(f"PASS {sum(checks.values())}/{len(checks)}")


if __name__ == "__main__":
    main()
