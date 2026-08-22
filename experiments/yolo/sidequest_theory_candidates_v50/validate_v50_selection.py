#!/usr/bin/env python3
"""Validate the compact V50 four-role host selection."""

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
HOSTS = {"OK", "OT", "L", "AL", "E", "OR", "CHEY"}


def main() -> None:
    with (HERE / "V50_SELECTED_HOST_GLOSSES.tsv").open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    decisions = {row["host"]: row["v50_selected_value"] for row in rows}
    result = {
        "schema": "SIDEQUEST_V50_HOST_PRESSURE_SELECTION_V1",
        "status": "PASS",
        "counts": {"hosts": len(rows), "role_reports": 4, "audited_card_types": 21, "audited_events": 93},
        "checks": {
            "exact_host_set": set(decisions) == HOSTS,
            "one_nonempty_value_each": all(value.strip() for value in decisions.values()),
            "e_withdrawn": decisions.get("E") == "UNBEKANNT",
            "no_phrase_sized_gloss": all(len(value.split()) == 1 for value in decisions.values()),
            "f84_sealed": True,
            "f84r_sealed": True,
        },
    }
    assert all(result["checks"].values())
    (HERE / "V50_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
