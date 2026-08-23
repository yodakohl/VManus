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
    instructions = rows("TWO_HUNDRED_SIXTY_FIRST_173_INSTRUCTION_COMPILER.tsv")
    surfaces = rows("TWO_HUNDRED_SIXTY_FIRST_230_SURFACE_DICTIONARY.tsv")
    events = rows("TWO_HUNDRED_SIXTY_FIRST_381_EVENT_ROUNDTRIP.tsv")
    statements = rows("TWO_HUNDRED_SIXTY_FIRST_116_STATEMENT_ROUNDTRIP.tsv")
    checks = {
        "173_unique_instructions": len(instructions) == 173 and len({r["source_instruction_de"] for r in instructions}) == 173,
        "173_unique_cards": len({r["master_card_id"] for r in instructions}) == 173,
        "230_unique_surfaces": len(surfaces) == 230 and len({r["visible_surface"] for r in surfaces}) == 230,
        "surface_maps_one_card": all(r["master_card_id"].strip() for r in surfaces),
        "34_multi_surface_cards": sum(int(r["registered_surface_count"]) > 1 for r in instructions) == 34,
        "381_events": len(events) == 381 and len({r["event_id"] for r in events}) == 381,
        "202_renderer_choice_events": sum(int(r["renderer_choice_count"]) > 1 for r in events) == 202,
        "all_event_roundtrips": all(r["master_roundtrip"] == "PASS" and r["instruction_roundtrip"] == "PASS" for r in events),
        "116_statement_roundtrips": len(statements) == 116 and all(r["roundtrip_status"] == "PASS" for r in statements),
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
