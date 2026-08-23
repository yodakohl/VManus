#!/usr/bin/env python3
"""Validate the three complete apprentice tracks."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


OUT = Path(__file__).resolve().parent


def read_tsv(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    traces = read_tsv("SEVENTY_EIGHTH_219_GROUP_FORWARD_BACKWARD_TRACE.tsv")
    statements = read_tsv("SEVENTY_EIGHTH_57_STATEMENT_OR_LOCUS_READINGS.tsv")
    tracks = read_tsv("SEVENTY_EIGHTH_3_COMPLETE_APPRENTICE_TRACKS.tsv")
    counts = Counter(row["track"] for row in traces)
    statement_counts = Counter(row["track"] for row in statements)
    checks = {
        "three_tracks": len(tracks) == 3 and {row["track"] for row in tracks} == {"H3", "B2", "A3"},
        "219_groups": len(traces) == 219 and len({row["trace_serial"] for row in traces}) == 219,
        "track_group_counts": counts == {"H3": 17, "B2": 62, "A3": 140},
        "57_statement_or_locus_rows": len(statements) == 57 and statement_counts == {"H3": 4, "B2": 22, "A3": 31},
        "all_forward_layers_present": all(all(row[key] for key in ("forward_1_segment", "forward_2_minimal_card", "forward_3_owner_or_namespace", "forward_4_licensed_source_slots", "forward_5_selected_unit_vocabulary", "forward_6_spoken_action")) for row in traces),
        "all_backward_forms_present": all(row["backward_1_required_address"] and row["backward_2_required_card_or_group"] for row in traces),
        "content_not_free": all(row["concrete_content_without_owner_or_local_source"] == "NOT_AVAILABLE" for row in traces),
        "sealed_pages_absent": all("f84" not in "\t".join(row.values()).lower() for row in traces + statements + tracks),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
