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
    events = rows("TWO_HUNDRED_FORTY_SECOND_281_EVENT_BIOLOGICAL_MANUAL.tsv")
    statements = rows("TWO_HUNDRED_FORTY_SECOND_97_STATEMENT_BIOLOGICAL_EDITION.tsv")
    dictionary = rows("TWO_HUNDRED_FORTY_SECOND_163_FORM_DICTIONARY.tsv")
    curriculum = rows("TWO_HUNDRED_FORTY_SECOND_COMPACT_CURRICULUM.tsv")
    checks = {
        "281_events": len(events) == 281,
        "281_unique_event_ids": len({r["event_id"] for r in events}) == 281,
        "97_statements": len(statements) == 97,
        "97_unique_statement_ids": len({r["statement_id"] for r in statements}) == 97,
        "six_records": {r["record_unit_id"] for r in statements} == {"B1", "B2", "B3", "B4", "B5", "B6"},
        "three_pages": {r["page"] for r in events} == {"f81v", "f82r", "f83r"},
        "163_forms": len(dictionary) == 163,
        "all_forms_invariant": all(r["value_invariant_across_all_occurrences"] == "YES" for r in dictionary),
        "all_event_defaults_concrete": all(r["concrete_default_de"].strip() for r in events),
        "all_statements_complete": all(r["complete_reading_de"].strip() for r in statements),
        "curriculum_22": len(curriculum) == 22,
        "seven_motifs": sum(r["lesson_layer"] == "PROCEDURE_MOTIF" for r in curriculum) == 7,
        "six_specialists": sum(r["lesson_layer"] == "SPECIALIST_COMPONENT" for r in curriculum) == 6,
        "six_whole_signs": sum(r["lesson_layer"] == "LEARNED_WHOLE_SIGN" for r in curriculum) == 6,
        "three_atomic": sum(r["lesson_layer"] == "ATOMIC_COMMAND" for r in curriculum) == 3,
        "no_unknown": all("UNKNOWN" not in "\t".join(r.values()) for r in events),
        "sealed_pages_absent": all("f84" not in "\t".join(r.values()).lower() for r in events),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        print(json.dumps(result, ensure_ascii=False, indent=2))
        raise SystemExit(1)
    print(f"PASS {sum(checks.values())}/{len(checks)}")


if __name__ == "__main__":
    main()
