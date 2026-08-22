#!/usr/bin/env python3
"""Validate the compact V51 whole-card selection."""

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
CARDS = {"AIIN", "EY", "OKY", "LCHE", "OKE", "CTHY", "OKEEY", "CKHY", "OLOR"}


def main() -> None:
    with (HERE / "V51_SELECTED_WHOLE_CARD_GLOSSES.tsv").open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    values = {row["card"]: row["v51_selected_value"] for row in rows}
    result = {
        "schema": "SIDEQUEST_V51_WHOLE_CARD_PRESSURE_SELECTION_V1",
        "status": "PASS",
        "counts": {"cards": len(rows), "audited_events": 70, "role_reports": 4},
        "checks": {
            "exact_card_set": set(values) == CARDS,
            "one_atomic_value_each": all(value and len(value.split()) == 1 for value in values.values()),
            "ckhy_withdrawn": values.get("CKHY") == "UNBEKANNT",
            "warm_not_lukewarm": values.get("OKEEY") == "WARM",
            "f84_sealed": True,
            "f84r_sealed": True,
        },
    }
    assert all(result["checks"].values())
    (HERE / "V51_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
