#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent
PREFIX = "EIGHT_HUNDRED_THIRTY_SIXTH"


def read(suffix: str) -> list[dict[str, str]]:
    with (HERE / f"{PREFIX}_{suffix}").open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    subprocess.run(["python", str(HERE / "build_eight_hundred_thirty_sixth.py")], check=True)
    pairs = read("27_AR_AL_OPERATOR_PAIRS.tsv")
    top = read("10_SOURCE_TARGET_PREDICTIONS.tsv")
    summary = json.loads((HERE / f"{PREFIX}_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    both = [row for row in pairs if row["ar_status"] == row["al_status"] == "ATTESTED"]
    one = [row for row in pairs if row["predicted_surface"] != "NONE"]
    checks = {
        "pair_inventory": len(pairs) == 27 and len({row["pair_id"] for row in pairs}) == 27,
        "attested_pair_count": len(both) == 5,
        "predicted_pair_count": len(one) == 22,
        "every_pair_normalized": all("AR" in row["ar_recipe"].split("+") and "AL" not in row["ar_recipe"].split("+") and "AL" in row["al_recipe"].split("+") and "AR" not in row["al_recipe"].split("+") for row in pairs),
        "operator_frames_match": all(row["ar_recipe"].replace("AR", "ADDRESS") == row["al_recipe"].replace("AL", "ADDRESS") == row["operator_frame"] for row in pairs),
        "top_inventory": len(top) == 10 and [int(row["rank"]) for row in top] == list(range(1, 11)),
        "top_are_one_sided": all(row["predicted_surface"] != "NONE" and row["use"] == "SEARCH_AS_SOURCE_TARGET_SWAP" for row in top),
        "existing_active_swaps": sum(row["already_active_prediction"] == "YES" for row in one) == 3 and {row["predicted_surface"] for row in one if row["already_active_prediction"] == "YES"} == {"chdar", "kchoal", "lal"},
        "no_component_change": summary["component_changes"] == 0,
        "sealed_pages": summary["sealed_pages"] == ["f84", "f84r"],
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / f"{PREFIX}_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
