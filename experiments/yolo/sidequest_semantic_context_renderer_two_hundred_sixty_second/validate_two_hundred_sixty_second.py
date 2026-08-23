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
    cards = rows("TWO_HUNDRED_SIXTY_SECOND_34_RENDERER_CARDS.tsv")
    traces = rows("TWO_HUNDRED_SIXTY_SECOND_202_RENDERER_TRACES.tsv")
    all_events = rows("TWO_HUNDRED_SIXTY_SECOND_381_GENERATED_SURFACES.tsv")
    rules = rows("TWO_HUNDRED_SIXTY_SECOND_THREE_RENDERER_RULES.tsv")
    modes = Counter(r["renderer_mode"] for r in all_events)
    owner = [r for r in traces if r["renderer_mode"] == "VISIBLE_OWNER_OVERRIDE"]
    checks = {
        "34_cards": len(cards) == 34 and len({r["master_card_id"] for r in cards}) == 34,
        "202_variant_events": len(traces) == 202 and len({r["event_id"] for r in traces}) == 202,
        "three_rules": len(rules) == 3,
        "381_events": len(all_events) == 381 and len({r["event_id"] for r in all_events}) == 381,
        "mode_split_179_198_4": modes == {"SOLE_REGISTERED_SURFACE": 179, "PAGE_POSITION_NEIGHBOUR_RENDERER": 198, "VISIBLE_OWNER_OVERRIDE": 4},
        "four_owner_events_exact": {r["event_id"] for r in owner} == {"E229", "E291", "E239", "E283"},
        "owner_cards_exact": {r["master_card_id"] for r in owner} == {"MC045", "MC025"},
        "all_renderer_pass": all(r["renderer_result"] == "PASS" and r["predicted_visible_surface"] == r["actual_visible_surface"] for r in traces),
        "all_surface_pass": all(r["result"] == "PASS" and r["generated_visible_surface"] == r["actual_visible_surface"] for r in all_events),
        "fixed_pages_only": {r["page"] for r in all_events} <= {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
        "sealed_pages_absent": all("f84" not in "\t".join(r.values()).lower() for r in all_events),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "VALIDATION.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        print(json.dumps(result, indent=2, ensure_ascii=False))
        raise SystemExit(1)
    print(f"PASS {sum(checks.values())}/{len(checks)}")


if __name__ == "__main__":
    main()
