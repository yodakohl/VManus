#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUTPUTS = [
    "EIGHT_HUNDRED_SIXTH_39_COMPONENT_THIRD_GRAMMAR.tsv",
    "EIGHT_HUNDRED_SIXTH_173_CARD_THIRD_DICTIONARY.tsv",
    "EIGHT_HUNDRED_SIXTH_381_EVENT_REPARSE.tsv",
    "EIGHT_HUNDRED_SIXTH_116_STATEMENT_REPARSE.tsv",
    "EIGHT_HUNDRED_SIXTH_64_UNATTESTED_PREDICTIONS.tsv",
    "EIGHT_HUNDRED_SIXTH_13_TEACHING_RULES.tsv",
    "EIGHT_HUNDRED_SIXTH_BUILD_SUMMARY.json",
]


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    subprocess.run(["python", str(HERE / "build_eight_hundred_sixth.py")], check=True)
    first = {name: digest(HERE / name) for name in OUTPUTS}
    subprocess.run(["python", str(HERE / "build_eight_hundred_sixth.py")], check=True)
    second = {name: digest(HERE / name) for name in OUTPUTS}
    components = read(OUTPUTS[0])
    cards = read(OUTPUTS[1])
    events = read(OUTPUTS[2])
    statements = read(OUTPUTS[3])
    predictions = read(OUTPUTS[4])
    rules = read(OUTPUTS[5])
    summary = json.loads((HERE / OUTPUTS[6]).read_text(encoding="utf-8"))
    checks = {
        "deterministic_rebuild": first == second,
        "counts_39_173_381_116": (len(components), len(cards), len(events), len(statements)) == (39, 173, 381, 116),
        "tiers_core22_strip9": summary["core_components"] == 22 and summary["strip_components"] == 9,
        "event_ids_complete": [row["event_id"] for row in events] == [f"E{i:03d}" for i in range(1, 382)],
        "card_ids_unique": len({row["exact_card_id"] for row in cards}) == 173,
        "statement_event_sum": sum(int(row["events"]) for row in statements) == 381,
        "core_touch_166_363": summary["core_touch_cards"] == 166 and summary["core_touch_events"] == 363,
        "fully_core_105_292": summary["fully_core_cards"] == 105 and summary["fully_core_events"] == 292,
        "revised_values_present": {row["component"]: row["short_value_de"] for row in components} | {} and all({row["component"]: row["short_value_de"] for row in components}[key] == value for key, value in {"O": "VORGANG", "SHED": "STEHENLASSEN", "P": "EINFUELLEN", "LSH": "SPUELEN"}.items()),
        "predictions_64_no_collision_one_dedup": len(predictions) == 64 and all(row["attested_on_fixed_pages"] == "NO" for row in predictions) and summary["prediction_source_proposals"] == 65 and summary["deduplicated_prediction_proposals"] == 1,
        "cheeeky_has_two_sources": set(next(row for row in predictions if row["predicted_surface"] == "cheeeky")["source"].split(",")) == {"PASS789_GRADE_HAND_BOARD", "PASS801_CHK_GRID"},
        "thirteen_rules": len(rules) == 13,
        "sealed_pages": summary["sealed_pages"] == ["f84", "f84r"],
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "output_sha256": second}
    (HERE / "EIGHT_HUNDRED_SIXTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
