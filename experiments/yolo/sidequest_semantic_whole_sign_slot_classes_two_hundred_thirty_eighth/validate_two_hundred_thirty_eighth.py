#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from pathlib import Path

OUT = Path(__file__).resolve().parent
ARTIFACTS = [
    "TWO_HUNDRED_THIRTY_EIGHTH_SEVEN_WHOLE_SIGN_OCCURRENCES.tsv",
    "TWO_HUNDRED_THIRTY_EIGHTH_SIX_SLOT_CLASSES.tsv",
    "TWO_HUNDRED_THIRTY_EIGHTH_SIX_REPLACEMENT_RULES.tsv",
    "TWO_HUNDRED_THIRTY_EIGHTH_READABLE_WHOLE_SIGN_CODEBOOK.md",
    "TWO_HUNDRED_THIRTY_EIGHTH_REPORT.md",
    "BUILD_SUMMARY.json",
]


def read(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def hashes() -> dict[str, str]:
    return {name: hashlib.sha256((OUT / name).read_bytes()).hexdigest() for name in ARTIFACTS}


def main() -> None:
    occurrences = read(ARTIFACTS[0])
    classes = read(ARTIFACTS[1])
    rules = read(ARTIFACTS[2])
    summary = json.loads((OUT / "BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "seven_occurrences": len(occurrences) == 7 and len({row["event_id"] for row in occurrences}) == 7,
        "six_signs": len(classes) == 6 and len({row["master_card_id"] for row in classes}) == 6,
        "three_actions_three_objects": summary["action_signs"] == 3 and summary["object_signs"] == 3,
        "six_unique_slots": len({row["slot_class"] for row in classes}) == 6,
        "six_prediction_rules": len(rules) == 6 and len({row["slot_class"] for row in rules}) == 6,
        "class_not_surface_predictable": all(row["card_class_predictable"] == "YES" and row["exact_surface_predictable"] == "NO" for row in classes),
        "contexts_complete": all(row["previous_value_de"] and row["next_value_de"] for row in occurrences),
        "sealed_not_accessed": summary["sealed_pages_accessed"] is False,
        "sealed_absent": "f84" not in " ".join((OUT / name).read_text(encoding="utf-8").lower() for name in ARTIFACTS[:-1]),
    }
    first = hashes()
    subprocess.run(["python3", str(OUT / "build_two_hundred_thirty_eighth.py")], check=True)
    second = hashes()
    checks["deterministic_rebuild"] = first == second
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "summary": summary, "artifact_sha256": second}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
