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
    cards = rows("TWO_HUNDRED_SIXTIETH_173_CARD_DICTIONARY.tsv")
    events = rows("TWO_HUNDRED_SIXTIETH_381_PROSE_EVENTS.tsv")
    statements = rows("TWO_HUNDRED_SIXTIETH_116_STATEMENTS.tsv")
    revisions = rows("TWO_HUNDRED_SIXTIETH_FOUR_CARD_REVISIONS.tsv")
    contexts = rows("TWO_HUNDRED_SIXTIETH_SEVEN_CONTEXTS.tsv")
    by_card = {r["master_card_id"]: r for r in cards}
    chd = [r for r in contexts if r["master_card_id"] == "MC088"]
    ched = [r for r in contexts if r["master_card_id"] == "MC005"]
    checks = {
        "173_unique_cores": len(cards) == 173 and len({r["portable_core_de"] for r in cards}) == 173,
        "381_events": len(events) == 381 and len({r["event_id"] for r in events}) == 381,
        "116_statements": len(statements) == 116,
        "four_revisions": len(revisions) == 4 and {r["master_card_id"] for r in revisions} == {"MC053", "MC163", "MC005", "MC088"},
        "seven_contexts": len(contexts) == 7 and len({r["event_id"] for r in contexts}) == 7,
        "chd_three_statement_only": len(chd) == 3 and all(r["previous_card"] == "STATEMENT_START" and r["next_card"] == "STATEMENT_END" for r in chd),
        "ched_two_left_contexts": len(ched) == 2 and all(r["previous_card"] != "STATEMENT_START" for r in ched),
        "otol_distinct": by_card["MC053"]["portable_core_de"] == "danach im selben Gang weiter" and by_card["MC163"]["portable_core_de"] == "zum Folgegang wechseln",
        "transfer_distinct": by_card["MC005"]["portable_core_de"] == "vorigen Posten überführen; Schluss" and by_card["MC088"]["portable_core_de"] == "neuen Posten einsetzen; Schluss",
        "seven_rewritten_statements": sum(r["revision_260"] == "REWRITTEN" for r in statements) == 7,
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
