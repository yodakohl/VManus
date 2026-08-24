#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    occ = read("FOUR_HUNDRED_FIFTEENTH_ETYD_OCCURRENCE.tsv")
    models = read("FOUR_HUNDRED_FIFTEENTH_FOUR_ETYD_MODELS.tsv")
    trace = read("FOUR_HUNDRED_FIFTEENTH_H1_FOURTEEN_EVENT_TRACE.tsv")
    statements = read("FOUR_HUNDRED_FIFTEENTH_TWO_H1_STATEMENTS.tsv")
    checks = {
        "one_etyd": len(occ) == 1 and occ[0]["event_id"] == "E010",
        "etyd_nonterminal": occ[0]["terminal"] == "NO",
        "gabe_selected": occ[0]["selected_whole_word_de"] == "Gabe",
        "four_models": len(models) == 4,
        "one_selected": [row["candidate"] for row in models if row["decision"] == "SELECT"] == ["GABE"],
        "fourteen_h1_events": len(trace) == 14,
        "exact_h1_order": [row["event_id"] for row in trace] == [f"E{i:03d}" for i in range(1, 15)],
        "handoff_pair": trace[9]["register_action"] == "CREATE_NEXT_ACTIVE_ITEM" and trace[10]["register_action"] == "REACTIVATE_CARRIED_ITEM",
        "two_statements": len(statements) == 2,
        "first_carries_gabe": statements[0]["end_state"] == "GABE_CARRIED_OPEN",
        "no_old_clause": all("Leib" not in value and "Wurzelvorrat" not in value for rows in (occ, models, trace, statements) for row in rows for value in row.values()),
        "sealed_pages_absent": all("f84" not in value.lower() for rows in (occ, models, trace, statements) for row in rows for value in row.values()),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FOUR_HUNDRED_FIFTEENTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(result)


if __name__ == "__main__":
    main()
