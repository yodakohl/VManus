#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    fields = read("HUNDRED_NINETY_THIRD_135_FIELD_FRAME_MODES.tsv")
    events = read("HUNDRED_NINETY_THIRD_381_EVENT_FRAME_TRACE.tsv")
    candidates = read("HUNDRED_NINETY_THIRD_20_MODE_FIELDS.tsv")
    modes = read("HUNDRED_NINETY_THIRD_MODE_SUMMARY.tsv")
    summary = json.loads((OUT / "BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "135_fields": len(fields) == 135 and len({row["field_id"] for row in fields}) == 135,
        "381_events": len(events) == 381 and len({row["event_id"] for row in events}) == 381,
        "20_candidate_fields": len(candidates) == 20,
        "field_event_sum": sum(int(row["event_count"]) for row in fields) == 381,
        "mode_partition": sum(int(row["fields"]) for row in modes) == 135,
        "candidate_ids_exact": {row["field_id"] for row in candidates} == {row["field_id"] for row in fields if row["field_frame_mode"] not in {"LOW_DATA", "MIXED"}},
        "candidate_support": all(int(row["mode_support_events"]) >= 2 for row in candidates),
        "event_field_modes_match": all(row["field_frame_mode"] == next(field["field_frame_mode"] for field in fields if field["field_id"] == row["field_id"]) for row in events),
        "allowed_pages": {row["page"] for row in events} == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
        "sealed_absent": summary["sealed_pages_accessed"] is False,
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "summary": summary}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
