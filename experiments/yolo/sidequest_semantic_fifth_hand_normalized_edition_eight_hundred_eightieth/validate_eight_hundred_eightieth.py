#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent
PREFIX = "EIGHT_HUNDRED_EIGHTIETH"


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    subprocess.run(["python", str(HERE / "build_eight_hundred_eightieth.py")], check=True)
    summary = json.loads((HERE / f"{PREFIX}_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    marks = read(f"{PREFIX}_438_MARK_FIFTH_HAND_EDITION.tsv")
    units = read(f"{PREFIX}_119_UNIT_FIFTH_HAND_EDITION.tsv")
    mappings = read(f"{PREFIX}_SURFACE_NORMALIZATION_MAP.tsv")
    orders = read(f"{PREFIX}_6_ORDER_NORMALIZATION_SUMMARY.tsv")
    inventory = read(f"{PREFIX}_4_SURFACE_INVENTORY_ROWS.tsv")
    checks = {
        "summary_pass": summary["status"] == "PASS",
        "marks_438": len(marks) == 438 and len({row["order_mark_id"] for row in marks}) == 438,
        "units_119": len(units) == 119,
        "orders_6": len(orders) == 6 and sum(int(row["marks"]) for row in orders) == 438,
        "identities_228": len({row["identity"] for row in marks}) == 228,
        "core_261": sum(row["card_class"] == "PORTABLE_CORE" for row in marks) == 261,
        "local_177_unchanged": sum(row["card_class"] == "LOCAL_MODEL" for row in marks) == 177 and all(row["original_surface"] == row["fifth_hand_surface"] for row in marks if row["card_class"] == "LOCAL_MODEL"),
        "normalized_68": sum(row["surface_action"] == "NORMALIZE_TO_HOUSE" for row in marks) == 68,
        "mappings_cover_68": sum(int(row["changed_marks"]) for row in mappings) == 68,
        "surface_types_247_to_208": summary["original_surface_types"] == 247 and summary["fifth_hand_surface_types"] == 208,
        "inventory_4": len(inventory) == 4 and {row["stage_class"] for row in inventory} == {"ALL", "PREP", "APP", "COND"},
        "meaning_fixed": all(row["meaning_changed"] == "NO" and row["concrete_default_de"] for row in marks) and all(row["meaning_changed"] == "NO" for row in units),
        "identity_fixed": all(row["identity_changed"] == "NO" for row in marks),
        "fixed_pages": summary["fixed_pages"] == ["f10r", "f11r", "f55v", "f56r", "f67r2", "f68r1", "f69v", "f81v", "f82r", "f83r"],
        "sealed": summary["sealed_pages"] == ["f84", "f84r"],
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / f"{PREFIX}_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
