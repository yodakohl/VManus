#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent
PREFIX = "EIGHT_HUNDRED_THIRTY_FOURTH"


def read(suffix: str) -> list[dict[str, str]]:
    with (HERE / f"{PREFIX}_{suffix}").open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    subprocess.run(["python", str(HERE / "build_eight_hundred_thirty_fourth.py")], check=True)
    candidates = read("8_HIDDEN_WORD_CANDIDATES.tsv")
    dy = read("89_DY_STATEMENTS.tsv")
    air = read("5_AIR_EVENTS.tsv")
    summary = json.loads((HERE / f"{PREFIX}_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "candidate_inventory": len(candidates) == 8,
        "dy_inventory": len(dy) == 89 and len({row["statement_id"] for row in dy}) == 89,
        "dy_step_split": sum(row["schritt_present"] == "YES" for row in dy) == 68 and sum(row["schritt_present"] == "NO" for row in dy) == 21,
        "dy_decision": all(row["decision"] == "SCHRITT_IS_FLUENT_OBJECT_OF_SCHLUSS" for row in dy),
        "air_inventory": len(air) == 5 and len({row["event_id"] for row in air}) == 5,
        "air_literal_water": all("WASSER" in row["literal_reading_de"] for row in air),
        "air_current_split": sum(row["revision"] == "FLUESSIGKEIT_TO_WASSER" for row in air) == 4 and sum(row["revision"] == "NONE" for row in air) == 1,
        "air_proposed_water": all("wasser" in row["proposed_working_reading_de"].lower() for row in air),
        "air_no_proposed_fluid": all("fluessigkeit" not in row["proposed_working_reading_de"].lower() for row in air),
        "no_component_revision": summary["new_component_revision"] == "NONE",
        "allowed_pages": {row["page"] for row in air + dy} <= {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
        "sealed_pages": summary["sealed_pages"] == ["f84", "f84r"],
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / f"{PREFIX}_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
