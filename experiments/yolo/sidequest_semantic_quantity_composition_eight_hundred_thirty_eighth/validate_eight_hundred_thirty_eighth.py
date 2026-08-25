#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
PREFIX = "EIGHT_HUNDRED_THIRTY_EIGHTH"


def read(suffix: str) -> list[dict[str, str]]:
    with (HERE / f"{PREFIX}_{suffix}").open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    subprocess.run(["python", str(HERE / "build_eight_hundred_thirty_eighth.py")], check=True)
    cards = read("21_QUANTITY_CARDS.tsv")
    events = read("61_QUANTITY_EVENTS.tsv")
    grid = read("18_OPERATOR_QUANTITY_FRAMES.tsv")
    new = read("3_NEW_IIN_PREDICTIONS.tsv")
    summary = json.loads((HERE / f"{PREFIX}_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    event_counts = Counter(row["quantity_component"] for row in events)
    checks = {
        "quantity_inventory": len(cards) == 21 and len(events) == 61 and len({row["exact_card_id"] for row in cards}) == 21 and len({row["event_id"] for row in events}) == 61,
        "quantity_counts": Counter(row["quantity_component"] for row in cards) == Counter({"AIIN": 10, "AIN": 8, "IIN": 3}) and event_counts == Counter({"AIIN": 39, "AIN": 18, "IIN": 4}),
        "quantity_values": {row["quantity_component"]: row["quantity_value_de"] for row in cards} == {"AIN": "PORTION", "AIIN": "SOLLMASS", "IIN": "STUFE"},
        "frame_inventory": len(grid) == 18,
        "ain_aiin_pair_frames": sum(row["ain_aiin_pair_available"] == "YES" for row in grid) == 14,
        "triad_frame": sum(row["three_cell_row_available"] == "YES" for row in grid) == 1 and next(row for row in grid if row["three_cell_row_available"] == "YES")["operator_frame"] == "K+QTY",
        "new_predictions": len(new) == 3 and {row["predicted_surface"] for row in new} == {"aiiin", "qokaiiin", "ykaiiin"} and all(row["status"] == "NEW_CREATIVE_PREDICTION" for row in new),
        "no_component_change": summary["component_changes"] == 0,
        "allowed_pages": {row["page"] for row in events} <= {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
        "sealed_pages": summary["sealed_pages"] == ["f84", "f84r"],
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / f"{PREFIX}_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
