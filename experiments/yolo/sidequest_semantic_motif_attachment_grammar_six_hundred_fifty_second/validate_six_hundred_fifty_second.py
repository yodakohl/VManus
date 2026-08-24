#!/usr/bin/env python3
"""Validate the source motif attachment grammar."""

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
    attachments = rows("SIX_HUNDRED_FIFTY_SECOND_28_MOTIF_ATTACHMENTS.tsv")
    motifs = rows("SIX_HUNDRED_FIFTY_SECOND_9_MOTIF_POSITION_CLASSES.tsv")
    readings = rows("SIX_HUNDRED_FIFTY_SECOND_25_ATTACHMENT_READINGS.tsv")
    counts = Counter(row["position_class"] for row in attachments)
    checks = {
        "twenty_eight_attachments": len(attachments) == 28,
        "nine_motifs": len(motifs) == 9,
        "twenty_five_statements": len(readings) == 25,
        "positions_partition": counts == {"ENTRY": 6, "MEDIAL": 13, "CLOSE": 8, "WHOLE_STATEMENT": 1},
        "source_order_unchanged": all(row["source_order_unchanged"] == "YES" for row in readings),
        "all_motifs_source_attested": all(row["all_instances_source_attested"] == "YES" for row in motifs),
        "all_attachment_signatures": all(">" in row["attachment_signature"] for row in attachments),
        "m04_always_closes": all(row["position_class"] == "CLOSE" for row in attachments if row["motif_id"] == "M04_CONTINUE_CLOSE"),
        "m07_always_closes": all(row["position_class"] == "CLOSE" for row in attachments if row["motif_id"] == "M07_TRANSFER_LONG_CLOSE"),
        "m05_always_medial": all(row["position_class"] == "MEDIAL" for row in attachments if row["motif_id"] == "M05_MEASURE_CONTINUATION"),
        "m09_all_four_positions": {row["position_class"] for row in attachments if row["motif_id"] == "M09_LONG_SET_BRANCH"} == {"ENTRY", "MEDIAL", "CLOSE", "WHOLE_STATEMENT"},
        "no_new_placeholder": all("UNKNOWN" not in row["motif_reading_de"] and "EXEMPLAR" not in row["motif_reading_de"] for row in attachments),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SIX_HUNDRED_FIFTY_SECOND_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for name, passed in checks.items():
        print(f"{name}\t{'PASS' if passed else 'FAIL'}")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
