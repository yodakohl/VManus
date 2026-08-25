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
    substitutions = read("SEVEN_HUNDRED_NINETY_THIRD_22_ADDRESS_SUBSTITUTIONS.tsv")
    paths = read("SEVEN_HUNDRED_NINETY_THIRD_44_BEFORE_AFTER_PATHS.tsv")
    invariants = read("SEVEN_HUNDRED_NINETY_THIRD_22_COMPONENT_INVARIANTS.tsv")
    rules = read("SEVEN_HUNDRED_NINETY_THIRD_5_ADDRESS_PATH_RULES.tsv")
    summary = json.loads((HERE / "SEVEN_HUNDRED_NINETY_THIRD_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "counts_22_44_22_5": (len(substitutions), len(paths), len(invariants), len(rules)) == (22, 44, 22, 5),
        "two_paths_each": all(sum(row["exercise"] == item["exercise"] for row in paths) == 2 for item in substitutions),
        "before_after_each": all({row["phase"] for row in paths if row["exercise"] == item["exercise"]} == {"BEFORE", "AFTER"} for item in substitutions),
        "all_address_reversed": all(row["address_change"] in {"AL→AR", "AR→AL"} for row in substitutions),
        "all_invariants_match": all(row["invariant_match"] == "YES" and row["source_invariant_components"] == row["target_invariant_components"] for row in invariants),
        "all_other_events_kept": all(row["other_events_unchanged"] == "YES" for row in substitutions),
        "path_orientation": all(("-->" in row["directed_path"] and ("::ZIEL" in row["directed_path"] if row["address"] == "AL" else "::QUELLE" in row["directed_path"])) for row in paths),
        "fixed_pages_sealed": all("f84" not in "\t".join(row.values()).lower() for rows in (substitutions, paths, invariants, rules) for row in rows),
        "summary_pass": summary == {
            "status": "PASS",
            "substitutions": 22,
            "before_after_paths": 44,
            "component_invariants": 22,
            "invariant_matches": 22,
            "other_events_preserved": 22,
            "decision": "AL_AR_SWAP_REVERSES_OWNER_LOCAL_PATH_AND_PRESERVES_OTHER_COMPONENTS",
        },
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_NINETY_THIRD_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
