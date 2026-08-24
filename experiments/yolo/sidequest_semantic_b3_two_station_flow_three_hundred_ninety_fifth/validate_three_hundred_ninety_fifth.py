#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    trace = read("THREE_HUNDRED_NINETY_FIFTH_SEVEN_EVENT_TWO_STATION_TRACE.tsv")
    reset = read("THREE_HUNDRED_NINETY_FIFTH_OWNER_RESET.tsv")
    stages = read("THREE_HUNDRED_NINETY_FIFTH_FOUR_LOCAL_STAGES.tsv")
    contrast = read("THREE_HUNDRED_NINETY_FIFTH_H4_B3_FLOW_CONTRAST.tsv")
    checks = {
        "seven_events": len(trace) == 7,
        "events_exact": {row["event_id"] for row in trace} == {f"E{number:03d}" for number in range(285, 292)},
        "owner_split": Counter(row["visible_owner_zone"] for row in trace) == {"B3_MARGIN_TO_MAIN_GAP_UNRESOLVED": 6, "B3_MAIN_ARCH_LINKED_PAIR": 1},
        "one_reset": len(reset) == 1 and reset[0]["after_event"] == "E290" and reset[0]["before_event"] == "E291",
        "no_visible_connection": reset[0]["physical_connection_visible"] == "NO",
        "no_material_carry": reset[0]["material_identity_carried"] == "NO_NOT_VISIBLE",
        "four_stages": len(stages) == 4,
        "no_direction_claims": all(row["physical_direction_claim"] == "NONE" for row in trace),
        "no_global_flow": all(row["global_flow_claim"] == "NONE" for row in trace),
        "two_contrast_rows": len(contrast) == 2,
        "local_continuity_before_reset": all(trace[index]["active_after"] == trace[index + 1]["active_before"] for index in range(5)),
        "reset_breaks_identity": trace[5]["active_after"] != trace[6]["active_before"],
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    payload = {"status": status, "checks": checks, "check_count": len(checks)}
    (HERE / "THREE_HUNDRED_NINETY_FIFTH_VALIDATION.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if status != "PASS":
        raise SystemExit(json.dumps(payload, ensure_ascii=False, indent=2))
    print(f"PASS {len(checks)} checks")


if __name__ == "__main__":
    main()
