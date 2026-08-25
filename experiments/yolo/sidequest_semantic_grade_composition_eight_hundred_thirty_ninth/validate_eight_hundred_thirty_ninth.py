#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
PREFIX = "EIGHT_HUNDRED_THIRTY_NINTH"


def read(suffix: str) -> list[dict[str, str]]:
    with (HERE / f"{PREFIX}_{suffix}").open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    subprocess.run(["python", str(HERE / "build_eight_hundred_thirty_ninth.py")], check=True)
    cards = read("53_GRADE_CARDS.tsv")
    events = read("91_GRADE_EVENTS.tsv")
    grid = read("54_OPERATOR_GRADE_FRAMES.tsv")
    strong = read("8_STRONG_GRADE_ROWS.tsv")
    predicted = read("7_GRADE_PREDICTIONS.tsv")
    summary = json.loads((HERE / f"{PREFIX}_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "grade_inventory": len(cards) == 53 and len(events) == 91 and len({row["exact_card_id"] for row in cards}) == 53 and len({row["event_id"] for row in events}) == 91,
        "grade_unique_counts": Counter(row["grade_component"] for row in cards) == Counter({"E": 34, "EE": 17, "EEE": 2}) and Counter(row["grade_component"] for row in events) == Counter({"E": 49, "EE": 40, "EEE": 2}),
        "grade_membership_counts": summary["grade_component_memberships_cards"] == 54 and summary["grade_component_memberships_events"] == 92,
        "grade_values": {row["grade_component"]: row["grade_value_de"] for row in cards} == {"E": "KURZ", "EE": "LANG", "EEE": "VOLL"},
        "frame_inventory": len(grid) == 54 and sum(int(row["attested_cells"]) > 0 for row in grid) == 42,
        "strong_rows": len(strong) == 8 and sum(int(row["attested_cells"]) == 3 for row in strong) == 1,
        "fully_attested_ok_close": any(row["operator_frame"] == "OK+GRADE+DY" and int(row["attested_cells"]) == 3 for row in strong),
        "prediction_inventory": len(predicted) == 7 and {row["predicted_surface"] for row in predicted if row["priority"] == "HIGH"} == {"cheeeky", "solkeeey"},
        "no_component_change": summary["component_changes"] == 0,
        "allowed_pages": {row["page"] for row in events} <= {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
        "sealed_pages": summary["sealed_pages"] == ["f84", "f84r"],
    }
    double = [row for row in cards if int(row["grade_token_count"]) == 2]
    checks["double_e_control"] = len(double) == 1 and double[0]["surfaces"] == "qekey" and double[0]["component_recipe"] == "E+K+E+Y"
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / f"{PREFIX}_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
