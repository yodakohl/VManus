#!/usr/bin/env python3
"""Validate motif consolidation and minimal statement rewrites."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    motifs = read("SIX_HUNDRED_FIFTY_FIRST_9_SOURCE_MOTIFS.tsv")
    instances = read("SIX_HUNDRED_FIFTY_FIRST_SELECTED_MOTIF_INSTANCES.tsv")
    readings = read("SIX_HUNDRED_FIFTY_FIRST_25_MINIMAL_STATEMENT_READINGS.tsv")
    suppressed = read("SIX_HUNDRED_FIFTY_FIRST_OVERLAP_SUPPRESSIONS.tsv")
    member_sequences = [member for row in motifs for member in row["member_constructions"].split(" || ")]
    checks = {
        "nine_motifs": len(motifs) == 9,
        "fifteen_members_once": len(member_sequences) == 15 and len(set(member_sequences)) == 15,
        "all_source_attested": all(row["source_attested"] == "YES" for row in motifs),
        "twenty_five_readings": len(readings) == 25,
        "all_events_accounted": all(row["all_events_accounted"] == "YES" and int(row["events_covered_by_motifs"]) + int(row["events_left_as_individual_cards"]) == int(row["event_count"]) for row in readings),
        "every_reading_has_motif": all(int(row["selected_motif_instances"]) >= 1 and row["selected_motifs"] for row in readings),
        "selected_instances_bound": len(instances) == sum(int(row["selected_motif_instances"]) for row in readings),
        "longest_first_trigram_selected": sum(row["n"] == "3" and row["card_sequence"] == "PROC019|PROC009|PROC019" for row in instances) == 2,
        "overlapping_pairs_suppressed": sum(row["card_sequence"] in {"PROC019|PROC009", "PROC009|PROC019"} for row in suppressed) >= 4,
        "no_placeholder_readings": all(row["minimal_source_reading_de"] and "UNKNOWN" not in row["minimal_source_reading_de"] for row in readings),
        "motif_ids_valid": all(row["motif_id"] in {motif["motif_id"] for motif in motifs} for row in instances),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SIX_HUNDRED_FIFTY_FIRST_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
