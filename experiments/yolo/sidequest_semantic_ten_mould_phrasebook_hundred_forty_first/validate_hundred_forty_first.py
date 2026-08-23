#!/usr/bin/env python3
import csv
import json
from collections import Counter
from pathlib import Path


OUT = Path(__file__).resolve().parent


def rows(name):
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    moulds = rows("HUNDRED_FORTY_FIRST_TEN_PHRASE_MOULDS.tsv")
    assignments = rows("HUNDRED_FORTY_FIRST_116_MOULD_ASSIGNMENTS.tsv")
    counts = Counter(r["mould_id"] for r in assignments)
    checks = {
        "moulds_10": len(moulds) == 10,
        "statements_116": len(assignments) == 116,
        "events_381": sum(int(r["event_count"]) for r in assignments) == 381,
        "all_moulds_used": set(counts) == {r["mould_id"] for r in moulds},
        "statement_ids_unique": len({r["statement_id"] for r in assignments}) == 116,
        "paired_measure_3": counts["M07_PAIRED_MEASURE_FRAME"] == 3,
        "carried_preparation_2": counts["M08_CARRIED_PREPARATION_FRAME"] == 2,
        "local_cells_13": counts["M10_LOCAL_EXACT_CELL"] == 13,
        "no_empty_cells": all(all(v for v in r.values()) for table in (moulds, assignments) for r in table),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "mould_counts": dict(sorted(counts.items()))}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
