#!/usr/bin/env python3
import csv
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent


def rows(name):
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    trace = rows("HUNDRED_NINETEENTH_381_EVENT_FOUR_HAND_TRACE.tsv")
    records = rows("HUNDRED_NINETEENTH_ELEVEN_RECORD_ASSIGNMENTS.tsv")
    hands = rows("HUNDRED_NINETEENTH_FOUR_SCRIBE_WORKLOADS.tsv")
    checks = {
        "events_381": len(trace) == 381,
        "records_11": len(records) == 11,
        "hands_4": len(hands) == 4,
        "events_unique": len({r["event_serial"] for r in trace}) == 381,
        "all_records_assigned": all(r["assigned_renderer"] in {"R-A", "R-B", "R-C", "R-D"} for r in records),
        "learning_mode_complete": all(r["learning_mode"] in {"MEMORIZE_SHARED_17", "MEMORIZE_RECURRENT_SECTION_CARD", "COPY_SINGLETON_FROM_MASTER"} for r in trace),
        "shared_17_each": all(r["shared_cards_memorized"] == "17" for r in hands),
        "master_corrects": next(r for r in hands if r["renderer_id"] == "R-A")["supervision_duty"] == "correct all 381 entries after copying",
        "counts_reconcile": sum(int(r["assigned_events"]) for r in hands) == 381,
        "sealed_absent": all("f84" not in "\t".join(r.values()).lower() for r in trace),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
