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
    statements = rows("TWO_HUNDRED_THIRTY_NINTH_FORTY_THREE_COMPLETE_STATEMENTS.tsv")
    events = rows("TWO_HUNDRED_THIRTY_NINTH_ONE_HUNDRED_TWENTY_EIGHT_PROTOCOL_EVENTS.tsv")
    protocols = rows("TWO_HUNDRED_THIRTY_NINTH_TWO_PROTOCOLS.tsv")
    checks = {
        "statement_count_43": len(statements) == 43,
        "event_count_128": len(events) == 128,
        "two_protocols": len(protocols) == 2,
        "statement_ids_unique": len({r["statement_id"] for r in statements}) == 43,
        "event_ids_unique": len({r["event_id"] for r in events}) == 128,
        "b1_21_statements": sum(r["record_unit_id"] == "B1" for r in statements) == 21,
        "b2_22_statements": sum(r["record_unit_id"] == "B2" for r in statements) == 22,
        "b1_66_events": sum(r["record_unit_id"] == "B1" for r in events) == 66,
        "b2_62_events": sum(r["record_unit_id"] == "B2" for r in events) == 62,
        "all_values_concrete": all(r["concrete_value_de"].strip() for r in events),
        "all_translations_complete": all(r["complete_translation_de"].strip() for r in statements),
        "b1_one_owner": len({r["visible_owner"] for r in statements if r["record_unit_id"] == "B1"}) == 1,
        "b2_five_owners": len({r["visible_owner"] for r in statements if r["record_unit_id"] == "B2"}) == 5,
        "only_fixed_pages": {r["page"] for r in events} == {"f81v", "f82r"},
        "no_sealed_pages": all("f84" not in "\t".join(r.values()).lower() for r in events),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "VALIDATION.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(1)
    print(f"PASS {sum(checks.values())}/{len(checks)}")


if __name__ == "__main__":
    main()
