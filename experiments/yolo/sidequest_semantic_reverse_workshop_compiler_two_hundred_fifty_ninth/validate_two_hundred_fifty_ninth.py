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
    instructions = rows("TWO_HUNDRED_FIFTY_NINTH_171_INSTRUCTION_ENTRIES.tsv")
    events = rows("TWO_HUNDRED_FIFTY_NINTH_381_REVERSE_GENERATED_EVENTS.tsv")
    statements = rows("TWO_HUNDRED_FIFTY_NINTH_116_REVERSE_GENERATED_STATEMENTS.tsv")
    routes = Counter(r["apprentice_route"] for r in statements)
    variant_instructions = [r for r in instructions if r["selection_class"] == "WORKING_EQUIVALENCE_SET"]
    checks = {
        "171_instructions": len(instructions) == 171 and len({r["workshop_instruction_de"] for r in instructions}) == 171,
        "169_unique_two_sets": sum(r["selection_class"] == "UNIQUE_CARD" for r in instructions) == 169 and len(variant_instructions) == 2,
        "variant_cards_exact": {r["candidate_card_ids"] for r in variant_instructions} == {"MC053|MC163", "MC005|MC088"},
        "381_events": len(events) == 381 and len({r["event_id"] for r in events}) == 381,
        "374_exact_7_variant_events": sum(r["master_selection"] == "EXACT_FROM_INSTRUCTION" for r in events) == 374,
        "116_statements": len(statements) == 116 and len({r["statement_id"] for r in statements}) == 116,
        "statement_routes_47_48_21": routes == {"FULLY_PRODUCTIVE": 47, "REQUIRES_LOCAL_CORE": 48, "REQUIRES_WHOLE_SIGN": 21},
        "109_exact_7_variant_statements": sum(r["master_card_roundtrip"] == "EXACT_UNIQUE" for r in statements) == 109,
        "all_semantic_pass": all(r["semantic_roundtrip"] == "PASS" for r in statements),
        "no_empty_sequences": all(r["generated_candidate_sequence"].strip() and r["actual_visible_sequence"].strip() for r in statements),
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
