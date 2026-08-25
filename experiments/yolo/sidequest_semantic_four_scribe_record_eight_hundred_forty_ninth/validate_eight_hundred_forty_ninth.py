#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent
PREFIX = "EIGHT_HUNDRED_FORTY_NINTH"


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    subprocess.run(["python", str(HERE / "build_eight_hundred_forty_ninth.py")], check=True)
    events = read(f"{PREFIX}_56_EVENT_RENDERINGS.tsv")
    statements = read(f"{PREFIX}_8_STATEMENT_RENDERINGS.tsv")
    records = read(f"{PREFIX}_4_COMPLETE_RECORDS.tsv")
    summary = json.loads((HERE / f"{PREFIX}_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    scribes = {"S1_BARE", "S2_CH", "S3_Q_SH", "S4_D_T"}
    event_ids = sorted({row["event_id"] for row in events})
    checks = {
        "inventory": len(events) == 56 and len(statements) == 8 and len(records) == 4,
        "scribes": {row["scribe"] for row in events} == scribes and {row["scribe"] for row in records} == scribes,
        "source_inventory": event_ids == [f"E{i:03d}" for i in range(1, 15)],
        "four_per_event": all(sum(row["event_id"] == event_id for row in events) == 4 for event_id in event_ids),
        "registered": all(row["registered_and_same_card"] == "YES" and row["rendered_surface"] in row["registered_variants"].split("|") for row in events),
        "same_card_order": all(row["same_card_order"] == "YES" for row in records),
        "same_statement_order": all(row["same_statement_order"] == "YES" for row in records),
        "same_decoded_record": len({row["decoded_record_de"] for row in records}) == 1 and all(row["same_decoded_record"] == "YES" for row in records),
        "boundaries": all(row["same_statement_boundary"] == "YES" for row in statements) and {row["statement_id"] for row in statements} == {"H1-S001", "H1-S002"},
        "variation": summary["profile_sensitive_positions"] == 7 and summary["invariant_positions"] == 7 and summary["changed_assignments"] == 18,
        "no_hand_attribution": summary["actual_hand_attributions"] == 0,
        "sealed_pages": summary["sealed_pages"] == ["f84", "f84r"],
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / f"{PREFIX}_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
