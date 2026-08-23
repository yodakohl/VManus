#!/usr/bin/env python3
"""Validate the ninety-seventh paradigm economy tables."""

from __future__ import annotations

import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    cells = rows("NINETY_SEVENTH_180_CELL_PARADIGM.tsv")
    families = rows("NINETY_SEVENTH_15_FAMILY_ECONOMY.tsv")
    collisions = rows("NINETY_SEVENTH_COLLISION_LEDGER.tsv")
    corrections = rows("NINETY_SEVENTH_R96_COMPOSITION_CORRECTIONS.tsv")
    checks = {
        "cells_180": len(cells) == 180,
        "cell_keys_unique": len({(row["head"], row["tail_class"]) for row in cells}) == 180,
        "families_15": len(families) == 15,
        "family_heads_unique": len({row["head"] for row in families}) == 15,
        "statuses_known": set(row["cell_status"] for row in cells) <= {"FILLED_VISIBLE_CELL", "FORWARD_PRODUCTIVE_GAP", "NO_LICENSED_COMBINATION_YET"},
        "filled_have_forms": all(row["observed_surfaces"] != "NONE" and int(row["observed_events"]) > 0 for row in cells if row["cell_status"] == "FILLED_VISIBLE_CELL"),
        "gaps_have_predictions": all(row["forward_sequences"] != "NONE" and row["observed_surfaces"] == "NONE" for row in cells if row["cell_status"] == "FORWARD_PRODUCTIVE_GAP"),
        "tiers_known": set(row["productivity_tier"] for row in families) <= {"BROAD_PRODUCTIVE_PARADIGM", "BOUNDED_PRODUCTIVE_PARADIGM", "NARROW_RECURRENT_PATTERN", "WHOLE_CARD_FIRST"},
        "collision_guarded": all(row["resolution"] == "LONGEST_REGISTERED_CARD_WINS" for row in collisions),
        "r96_observed_predictions_27": len(corrections) == 27,
        "taiin_alias_corrected": any(row["prediction_id"] == "P24" and row["reconciliation_verdict"] == "WITHDRAW_MATCH__RENDERER_ALIAS_NOT_COMPOUND" for row in corrections),
        "r96_reconciliation_23_2_2": (
            sum(row["reconciliation_verdict"].startswith("SUPPORTED") for row in corrections) == 23
            and sum(row["reconciliation_verdict"] == "MIXED_SURFACE_FAMILY_REQUIRES_WHOLE_CARD_CHECK" for row in corrections) == 2
            and sum(row["reconciliation_verdict"] == "WITHDRAW_MATCH__RENDERER_ALIAS_NOT_COMPOUND" for row in corrections) == 2
        ),
        "sealed_absent": all("f84" not in "\t".join(row.values()).lower() for row in cells + collisions),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
