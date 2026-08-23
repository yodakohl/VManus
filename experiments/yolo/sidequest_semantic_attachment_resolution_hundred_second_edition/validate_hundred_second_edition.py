#!/usr/bin/env python3
"""Validate the resolved attachment layer."""

from __future__ import annotations

import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    events = rows("HUNDRED_SECOND_381_RESOLVED_ATTACHMENTS.tsv")
    decisions = rows("HUNDRED_SECOND_27_AMBIGUOUS_DECISIONS.tsv")
    statements = rows("HUNDRED_SECOND_116_RESOLVED_STATEMENTS.tsv")
    checks = {
        "events_381": len(events) == 381,
        "event_serials_complete": [int(row["event_serial"]) for row in events] == list(range(1, 382)),
        "decisions_27": len(decisions) == 27,
        "decision_events_unique": len({row["event_id"] for row in decisions}) == 27,
        "statements_116": len(statements) == 116,
        "all_hosts_selected": all(row["selected_host_event"] != "NONE" for row in events),
        "all_equal_distance_resolved": sum(row["was_equal_distance"] == "YES" for row in events) == 27,
        "directions_binary_for_decisions": set(row["selected_direction"] for row in decisions) <= {"BACKWARD", "FORWARD"},
        "material_forward_rule": all(row["selected_direction"] == "FORWARD" for row in decisions if row["selection_rule"] == "MATERIAL_OR_STATE_BETWEEN_ACTIONS_FEEDS_NEXT_ACTION"),
        "no_dictionary_mutation": all(row["atomic_default_de"] for row in events),
        "sealed_absent": all("f84" not in "\t".join(row.values()).lower() for row in events),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
