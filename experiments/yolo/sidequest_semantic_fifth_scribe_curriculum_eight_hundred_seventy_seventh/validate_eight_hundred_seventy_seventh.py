#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent
PREFIX = "EIGHT_HUNDRED_SEVENTY_SEVENTH"


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    subprocess.run(["python", str(HERE / "build_eight_hundred_seventy_seventh.py")], check=True)
    summary = json.loads((HERE / f"{PREFIX}_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    core = read(f"{PREFIX}_56_PORTABLE_CORE_CARDS.tsv")
    local = read(f"{PREFIX}_172_LOCAL_MODEL_CARDS.tsv")
    components = read(f"{PREFIX}_29_COMPONENT_LESSON.tsv")
    products = read(f"{PREFIX}_4_PRODUCT_HANDLES.tsv")
    owners = read(f"{PREFIX}_16_OWNER_STATES.tsv")
    switches = read(f"{PREFIX}_10_OWNER_SWITCHES.tsv")
    conditions = read(f"{PREFIX}_6_CONDITION_HANDLES.tsv")
    calibrations = read(f"{PREFIX}_6_HOUSE_CALIBRATIONS.tsv")
    lessons = read(f"{PREFIX}_8_LESSON_CURRICULUM.tsv")
    all_cards = core + local
    checks = {
        "summary_pass": summary["status"] == "PASS",
        "all_438_marks_accounted": sum(int(row["visible_marks"]) for row in all_cards) == 438,
        "all_228_identities_partitioned": len(all_cards) == 228 and len({row["identity"] for row in all_cards}) == 228,
        "core_56": len(core) == 56,
        "core_crosses_orders": all(int(row["order_count"]) >= 2 for row in core),
        "core_261_marks": sum(int(row["visible_marks"]) for row in core) == 261,
        "local_172": len(local) == 172,
        "local_one_order": all(int(row["order_count"]) == 1 for row in local),
        "local_104_prose_marks": sum(int(row["visible_marks"]) for row in local if row["stage_classes"] != "COND") == 104,
        "local_73_condition_marks": sum(int(row["visible_marks"]) for row in local if row["stage_classes"] == "COND") == 73,
        "components_29": len(components) == 29 and all(row["short_value_de"] for row in components),
        "products_4": len(products) == 4,
        "owner_states_16": len(owners) == 16,
        "owner_switches_10": len(switches) == 10 and all(row["entry_kind"] == "SWITCH_AT_THIS_UNIT" for row in switches),
        "conditions_6": len(conditions) == 6 and sum(int(row["visible_groups_on_model_leaf"]) for row in conditions) == 73,
        "calibrations_6": len(calibrations) == 6,
        "lessons_8": len(lessons) == 8,
        "six_orders_in_core": {order for row in core for order in row["orders"].split(",")} == {f"WH{i:02d}" for i in range(1, 7)},
        "no_empty_values": all(row["concrete_default_de"] for row in all_cards),
        "fixed_pages_only": summary["fixed_pages"] == ["f10r", "f11r", "f55v", "f56r", "f67r2", "f68r1", "f69v", "f81v", "f82r", "f83r"],
        "sealed": summary["sealed_pages"] == ["f84", "f84r"],
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / f"{PREFIX}_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
