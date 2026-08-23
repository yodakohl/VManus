#!/usr/bin/env python3
import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def rows(name):
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    events = rows("HUNDRED_SIXTY_SEVENTH_36_EVENT_B4_PROCEDURE.tsv")
    clauses = rows("HUNDRED_SIXTY_SEVENTH_13_CLAUSE_B4_PROCEDURE.tsv")
    bridges = rows("HUNDRED_SIXTY_SEVENTH_10_B2_B4_CARD_BRIDGES.tsv")
    models = rows("HUNDRED_SIXTY_SEVENTH_3_PURPOSE_MODELS.tsv")
    checks = {
        "events_36": len(events) == 36,
        "serial_range_326_361": [int(row["event_serial"]) for row in events] == list(range(326, 362)),
        "clauses_13": len(clauses) == 13,
        "statement_ids_exact": [row["statement_id"] for row in clauses] == [f"B4-S{i:03d}" for i in range(4, 17)],
        "bridges_10": len(bridges) == 10,
        "three_all_record_bridges": sum(row["also_in_H3"] == "YES" for row in bridges) == 3,
        "models_3": len(models) == 3,
        "one_selected": sum(row["selected"] == "YES" for row in models) == 1,
        "selected_hybrid": any(row["model"] == "TREATMENT_CHARGE_THROUGH_LOCAL_APPARATUS" and row["selected"] == "YES" for row in models),
        "all_events_translated": all(row["complete_clause_translation_de"] for row in events),
        "all_clauses_translated": all(row["fluent_procedure_de"] for row in clauses),
        "fixed_page": {row["page"] for row in events} == {"f83r"},
        "no_empty_cells": all(all(value for value in row.values()) for table in (events, clauses, bridges, models) for row in table),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
