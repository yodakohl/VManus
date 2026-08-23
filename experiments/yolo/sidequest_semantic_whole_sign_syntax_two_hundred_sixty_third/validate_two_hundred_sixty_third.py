#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent


def rows(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    cards = rows("TWO_HUNDRED_SIXTY_THIRD_173_CARD_DICTIONARY.tsv")
    events = rows("TWO_HUNDRED_SIXTY_THIRD_381_PROSE_EVENTS.tsv")
    statements = rows("TWO_HUNDRED_SIXTY_THIRD_116_STATEMENTS.tsv")
    syntax = rows("TWO_HUNDRED_SIXTY_THIRD_23_WHOLE_SIGN_SYNTAX.tsv")
    occ = rows("TWO_HUNDRED_SIXTY_THIRD_28_WHOLE_SIGN_OCCURRENCES.tsv")
    card_classes = Counter(r["whole_sign_class"] for r in syntax)
    event_classes = Counter(r["whole_sign_class"] for r in occ)
    terminal = [r for r in occ if r["whole_sign_class"] == "TERMINAL_OPERATION_SIGN"]
    open_rows = [r for r in occ if r["whole_sign_class"] != "TERMINAL_OPERATION_SIGN"]
    by_id = {r["master_card_id"]: r for r in cards}
    checks = {
        "full_counts": len(cards) == 173 and len(events) == 381 and len(statements) == 116,
        "23_whole_signs": len(syntax) == 23 and len({r["master_card_id"] for r in syntax}) == 23,
        "28_occurrences": len(occ) == 28 and len({r["event_id"] for r in occ}) == 28,
        "card_class_split_10_4_1_8": card_classes == {"CONTENT_OR_PRODUCT_SIGN": 10, "INTERNAL_OPERATION_SIGN": 4, "OPEN_HANDOFF_SIGN": 1, "TERMINAL_OPERATION_SIGN": 8},
        "event_class_split_15_4_1_8": event_classes == {"CONTENT_OR_PRODUCT_SIGN": 15, "INTERNAL_OPERATION_SIGN": 4, "OPEN_HANDOFF_SIGN": 1, "TERMINAL_OPERATION_SIGN": 8},
        "terminal_slots_exact": all(r["terminal_status"] == "TERMINAL" and r["statement_position"] in {"LAST", "ONLY"} for r in terminal),
        "open_slots_nonclose": all(r["terminal_status"] == "NONCLOSE" for r in open_rows),
        "talam_revised": by_id["MC160"]["portable_core_de"] == "verwahren; Schluss",
        "one_rewritten_statement": sum(r["revision_263"] == "REWRITTEN" for r in statements) == 1,
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
