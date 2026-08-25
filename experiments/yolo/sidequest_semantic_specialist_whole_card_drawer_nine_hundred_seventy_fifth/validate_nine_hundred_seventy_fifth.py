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
    drawer = read("PASS975_SPECIALIST_CARD_DRAWER.tsv")
    events = read("PASS975_2511_EVENT_HYBRID_EDITION.tsv")
    passages = read("PASS975_SPECIALIST_PASSAGES.tsv")
    applied = [r for r in events if r["specialist_headword_de"]]
    h3 = next((r for r in passages if r["statement_id"] == "H3-S001"), None)
    checks = {
        "drawer_has_local_and_common_whole_cards": len(drawer) >= 65,
        "events_2511": len(events) == 2511,
        "event_ids_unique": len({r["event_id"] for r in events}) == 2511,
        "specialist_events_exist": len(applied) >= 50,
        "all_hybrid_readings": all(r["hybrid_working_reading_de"] for r in events),
        "specialist_priority_exact": all(r["reading_priority"] == "LOCAL_SPECIALIST_WHOLE_CARD" for r in applied),
        "anchor_passage_present": h3 is not None,
        "anchor_seven_cards": h3 is not None and int(h3["specialist_card_count"]) == 7,
        "anchor_sequence_exact": h3 is not None and h3["surface_sequence"] == "tshol schoal cfhy shfydaiin cphy shey tchody",
        "sealed_absent": all("f84" not in r["pages"].lower() for r in drawer)
        and all("f84" not in r["physical_page"].lower() for r in events + passages),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "specialist_applied_events": len(applied)}
    (HERE / "PASS975_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
