#!/usr/bin/env python3
import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def rows(name):
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    events = rows("HUNDRED_SIXTY_FIFTH_5_EVENT_DOUBLE_PASS.tsv")
    models = rows("HUNDRED_SIXTY_FIFTH_3_DOUBLE_PASS_MODELS.tsv")
    clauses = rows("HUNDRED_SIXTY_FIFTH_4_AFFECTED_CLAUSES.tsv")
    checks = {
        "events_5": len(events) == 5,
        "serials_exact": [row["event_serial"] for row in events] == ["327", "328", "329", "330", "331"],
        "fields_3": len({row["field_id"] for row in events}) == 3,
        "one_locus": {row["locus"] for row in events} == {"f83r.27"},
        "two_identical_pass_cards": [row["visible_surface"] for row in events[-2:]] == ["shckhedy", "shckhedy"],
        "two_pass_values_current": all(row["atomic_value_de"] == "durchlassen; Schluss" for row in events[-2:]),
        "models_3": len(models) == 3,
        "one_selected": sum(row["selection"] == "SELECTED" for row in models) == 1,
        "dittography_live": any(row["model"] == "ACCIDENTAL_DITTOGRAPHY" and row["selection"] == "LIVE_RIVAL" for row in models),
        "clauses_4": len(clauses) == 4,
        "no_card_value_change": all("durchlassen; Schluss" in row["atomic_card_chain_de"] for row in clauses if row["statement_id"] in {"B1-S020", "B4-S006", "B4-S007"}),
        "no_empty_cells": all(all(value for value in row.values()) for table in (events, models, clauses) for row in table),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
