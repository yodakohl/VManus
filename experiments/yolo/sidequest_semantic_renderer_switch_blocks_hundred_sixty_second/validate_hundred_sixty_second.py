#!/usr/bin/env python3
import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def rows(name):
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    blocks = rows("HUNDRED_SIXTY_SECOND_3_HAND_SWITCH_BLOCKS.tsv")
    trace = rows("HUNDRED_SIXTY_SECOND_251_FINAL_RENDER_TRACE.tsv")
    residual = rows("HUNDRED_SIXTY_SECOND_36_LOCAL_EXEMPLAR_SPELLINGS.tsv")
    records = rows("HUNDRED_SIXTY_SECOND_11_RECORD_RENDER_SUMMARY.tsv")
    checks = {
        "blocks_3": len(blocks) == 3,
        "block_events_6": sum(int(row["event_count"]) for row in blocks) == 6,
        "events_251": len(trace) == 251,
        "events_unique": len({row["event_serial"] for row in trace}) == 251,
        "habit_matches_215": sum(row["habit_match"] == "YES" for row in trace) == 215,
        "exact_surfaces_193": sum(row["exact_surface_match"] == "YES" for row in trace) == 193,
        "second_spellings_22": sum(row["apprentice_treatment"] == "SECOND_REGISTERED_SPELLING" for row in trace) == 22,
        "local_exemplar_spellings_36": len(residual) == 36,
        "records_11": len(records) == 11,
        "all_master_recovery_exact": all(row["master_recovery"] == "EXACT" for row in trace),
        "record_counts_reconcile": sum(int(row["shared_events"]) for row in records) == 251,
        "semantic_changes_none": all(row["semantic_change"] == "NONE" for row in blocks),
        "no_empty_cells": all(all(value for value in row.values()) for table in (blocks, trace, residual, records) for row in table),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
