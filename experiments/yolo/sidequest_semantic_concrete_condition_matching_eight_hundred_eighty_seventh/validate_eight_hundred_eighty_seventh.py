#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent
PREFIX = "EIGHT_HUNDRED_EIGHTY_SEVENTH"


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    subprocess.run(["python", str(HERE / "build_eight_hundred_eighty_seventh.py")], check=True)
    summary = json.loads((HERE / f"{PREFIX}_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    conditions = read(f"{PREFIX}_6_CONCRETE_CONDITION_HANDLES.tsv")
    groups = read(f"{PREFIX}_73_COMPLETE_CONDITION_GROUPS.tsv")
    matrix = read(f"{PREFIX}_36_CONDITION_APPLICATION_MATRIX.tsv")
    links = read(f"{PREFIX}_6_SELECTED_WHEN_LINKS.tsv")
    orders = read(f"{PREFIX}_6_CONCRETE_ORDER_HEADERS.tsv")
    checks = {
        "summary_pass": summary["status"] == "PASS",
        "conditions_6": len(conditions) == 6,
        "groups_73": len(groups) == 73 and len({row["opaque_local_id"] for row in groups}) == 73,
        "group_counts": [int(row["groups"]) for row in conditions] == [3, 1, 1, 1, 38, 29],
        "matrix_36": len(matrix) == 36,
        "one_selected_each": all(sum(row["biological_record"] == record and row["selected"] == "YES" for row in matrix) == 1 for record in {row["biological_record"] for row in links}),
        "links_6": len(links) == 6 and len(orders) == 6,
        "mapping_unchanged": summary["selected_mapping"] == {"B1": "C5@f69v.2", "B2": "C4@f69v.12", "B3": "C2@f67r2.15", "B4": "C6@f69v.3", "B5": "C3@f68r1.9", "B6": "C1@f67r2.1"},
        "zero_changes": summary["condition_changes"] == 0 and all(row["condition_changed"] == "NO" for row in orders),
        "all_complete_copy": all(row["copy_rule"] == "COPY_COMPLETE_LOCAL_LOCUS" for row in groups),
        "no_orientation": all(row["requires_start_or_direction"] == "NO" for row in conditions),
        "no_external_names": all(row["external_name_required"] == "NO" for row in conditions),
        "concrete": all(row["short_condition_de"] and row["expanded_condition_de"] for row in conditions) and all(row["complete_concrete_order_de"] for row in orders),
        "no_new_group_meanings": summary["new_group_meanings"] == 0,
        "sealed": summary["sealed_pages"] == ["f84", "f84r"],
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / f"{PREFIX}_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
