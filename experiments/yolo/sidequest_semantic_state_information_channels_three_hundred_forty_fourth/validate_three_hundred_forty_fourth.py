#!/usr/bin/env python3

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def rows(name):
    with (HERE / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


events = rows("THREE_HUNDRED_FORTY_FOURTH_381_EVENT_STATE_CHANNEL_AUDIT.tsv")
states = rows("THREE_HUNDRED_FORTY_FOURTH_FIVE_STATE_MARKER_SUMMARY.tsv")
channels = rows("THREE_HUNDRED_FORTY_FOURTH_ELEVEN_TRANSITION_CHANNELS.tsv")
explicit = [row for row in events if row["material_state_marker"] != "NONE"]
checks = {
    "all_381_events": len(events) == 381 and len({row["event_id"] for row in events}) == 381,
    "seventy_nine_explicit_markers": len(explicit) == 79,
    "three_hundred_two_other_events": len(events) - len(explicit) == 302,
    "five_state_summaries": len(states) == 5,
    "state_counts_reconcile": sum(int(row["explicit_marker_events"]) for row in states) == 79,
    "eleven_transition_channels": len(channels) == 11,
    "all_meanings_retained": all(row["meaning_retained"] == "YES" for row in channels),
    "at_least_one_owner_only_source": any("OWNER_SUPPLIES_STATE" in row["source_information_channels"] for row in channels),
    "at_least_one_explicit_target": any(row["target_information_channel"].startswith("CARD_EXPLICIT") for row in channels),
    "fixed_pages_only": {row["page"] for row in events} == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
    "sealed_absent": all(row["page"] not in {"f84", "f84r"} for row in events),
}
result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
(HERE / "THREE_HUNDRED_FORTY_FOURTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
if result["status"] != "PASS":
    raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
print("PASS", len(checks), "checks")
