#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    drills = read("THREE_HUNDRED_SIXTY_THIRD_159_DICTATION_DRILLS.tsv")
    events = read("THREE_HUNDRED_SIXTY_THIRD_380_EVENT_SETTING_ROUTES.tsv")
    ambiguous = read("THREE_HUNDRED_SIXTY_THIRD_AMBIGUOUS_BUNDLES.tsv")
    checks = {
        "159_drills": len(drills) == 159 and len({r["target_controlled_phrase"] for r in drills}) == 159,
        "all_drills_decided": all(r["status"] in {"COMPOSED_UNIQUE", "MASTER_CARD_REQUIRED"} for r in drills),
        "unique_has_one_candidate": all((int(r["candidate_count"]) == 1) == (r["status"] == "COMPOSED_UNIQUE") for r in drills),
        "380_events": len(events) == 380 and len({r["source_position_id"] for r in events}) == 380,
        "all_events_routed": all(r["setting_route"] in {"COMPOSE_FROM_CUES", "FETCH_WHOLE_CARD_FROM_BOARD"} for r in events),
        "ambiguous_only": all(int(r["candidate_count"]) > 1 for r in ambiguous),
        "ambiguous_counts_match": sum(int(r["candidate_count"]) for r in ambiguous) == sum(r["status"] == "MASTER_CARD_REQUIRED" for r in drills),
        "all_records": {r["record_unit_id"] for r in events} == {"H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"},
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    result = {"status": status, "checks": checks, "check_count": len(checks)}
    (HERE / "THREE_HUNDRED_SIXTY_THIRD_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if status != "PASS": raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"PASS {len(checks)} checks")


if __name__ == "__main__":
    main()
