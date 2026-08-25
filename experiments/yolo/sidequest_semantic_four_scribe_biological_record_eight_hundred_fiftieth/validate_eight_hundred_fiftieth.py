#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent
PREFIX = "EIGHT_HUNDRED_FIFTIETH"


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    subprocess.run(["python", str(HERE / "build_eight_hundred_fiftieth.py")], check=True)
    events = read(f"{PREFIX}_248_EVENT_RENDERINGS.tsv")
    statements = read(f"{PREFIX}_88_STATEMENT_RENDERINGS.tsv")
    records = read(f"{PREFIX}_4_COMPLETE_B2_RECORDS.tsv")
    summary = json.loads((HERE / f"{PREFIX}_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    scribes = {"S1_BARE", "S2_CH", "S3_Q_SH", "S4_D_T"}
    source_ids = {row["event_id"] for row in events}
    checks = {
        "inventory": len(events) == 248 and len(statements) == 88 and len(records) == 4,
        "source_shape": len(source_ids) == 62 and summary["distinct_exact_cards"] == 46 and summary["source_statements"] == 22,
        "scribes": {row["scribe"] for row in events} == scribes,
        "four_per_event": all(sum(row["event_id"] == event_id for row in events) == 4 for event_id in source_ids),
        "registered": all(row["registered_and_same_card"] == "YES" and row["rendered_surface"] in row["registered_variants"].split("|") for row in events),
        "structure": all(row["events"] == "62" and row["statements"] == "22" and row["owner_blocks"] == "5" and row["closes"] == "19" for row in records),
        "same_orders": all(row["same_card_order"] == row["same_statement_order"] == row["same_owner_order"] == row["same_decoded_record"] == "YES" for row in records),
        "statement_bindings": all(row["same_statement_and_owner"] == "YES" for row in statements) and len({row["statement_id"] for row in statements}) == 22,
        "variation": summary["profile_sensitive_positions"] == 28 and summary["invariant_positions"] == 34 and summary["changed_assignments"] > 0,
        "no_semantic_disagreement": summary["semantic_disagreements"] == 0,
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
