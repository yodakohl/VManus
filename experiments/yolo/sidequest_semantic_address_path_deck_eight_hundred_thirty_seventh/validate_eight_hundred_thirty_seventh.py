#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent
PREFIX = "EIGHT_HUNDRED_THIRTY_SEVENTH"


def read(suffix: str) -> list[dict[str, str]]:
    with (HERE / f"{PREFIX}_{suffix}").open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    subprocess.run(["python", str(HERE / "build_eight_hundred_thirty_seventh.py")], check=True)
    active = read("30_REBALANCED_ACTIVE_SURFACES.tsv")
    cards = read("9_CKH_CARDS.tsv")
    events = read("14_CKH_EVENTS.tsv")
    statements = read("12_CKH_STATEMENTS.tsv")
    path_predictions = read("2_SOURCE_PATH_PREDICTIONS.tsv")
    summary = json.loads((HERE / f"{PREFIX}_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "active_deck_preserved": len(active) == 30 and len({row["component_recipe"] for row in active}) == 24,
        "address_swaps_promoted": [row["predicted_surface"] for row in active[:3]] == ["chdar", "lal", "kchoal"] and all(row["address_path_status"] == "PROMOTED_AR_AL_SWAP" for row in active[:3]),
        "ckh_inventory": len(cards) == 9 and len(events) == 14 and len(statements) == 12,
        "ckh_constant": all(row["ckh_value"] == "DURCHLASS" for row in cards) and all("DURCHLASS" in row["reading_de"] for row in events),
        "ckh_target_context": sum(int(row["al_count"]) > 0 for row in statements) == 6,
        "source_path_target_context": sum(int(row["ar_count"]) > 0 and int(row["al_count"]) > 0 for row in statements) == 1,
        "path_predictions": len(path_predictions) == 2 and {row["predicted_surface"] for row in path_predictions} == {"chckhar", "sheckhar"},
        "no_component_change": summary["component_changes"] == 0,
        "allowed_pages": {row["page"] for row in events + statements} <= {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
        "sealed_pages": summary["sealed_pages"] == ["f84", "f84r"],
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / f"{PREFIX}_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
