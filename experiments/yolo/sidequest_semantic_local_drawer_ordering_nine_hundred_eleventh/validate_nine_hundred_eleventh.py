#!/usr/bin/env python3
"""Validate the Pass-911 local-drawer ordering."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
P910 = ROOT / "experiments/yolo/sidequest_semantic_three_layer_master_handbook_nine_hundred_tenth"
OUT = BASE / "PASS911_VALIDATION.json"


def read_tsv(name: str) -> list[dict[str, str]]:
    with (BASE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


checks: list[dict[str, object]] = []


def check(name: str, condition: bool, detail: object) -> None:
    checks.append({"name": name, "pass": bool(condition), "detail": detail})


def main() -> None:
    source = []
    with (P910 / "PASS910_LOCAL_NOMENCLATOR.tsv").open(encoding="utf-8", newline="") as handle:
        source = list(csv.DictReader(handle, delimiter="\t"))
    ordered = read_tsv("PASS911_ORDERED_LOCAL_DRAWER.tsv")
    workshop = read_tsv("PASS911_REVISED_WORKSHOP_CARDS.tsv")
    families = read_tsv("PASS911_RECURRENT_FAMILIES.tsv")
    cph = read_tsv("PASS911_CPH_FAMILY.tsv")

    check("source_240", len(source) == 240, len(source))
    check("ordered_240", len(ordered) == 240, len(ordered))
    check("same_codes", {row["local_code"] for row in source} == {row["local_code"] for row in ordered}, len(ordered))
    check("source_events_261", sum(int(row["events"]) for row in source) == 261, sum(int(row["events"]) for row in source))
    check("ordered_events_261", sum(int(row["events"]) for row in ordered) == 261, sum(int(row["events"]) for row in ordered))
    check("workshop_57", len(workshop) == 57, len(workshop))
    check("workshop_events_63", sum(int(row["events"]) for row in workshop) == 63, sum(int(row["events"]) for row in workshop))
    check("owner_labels_183", sum(row["old_drawer"] == "PICTURED_NAME_OR_CLASS" for row in ordered) == 183, Counter(row["old_drawer"] for row in ordered))
    check("no_whole_recipe", all(not row["revised_recipe"].startswith("WHOLE[") for row in ordered), "all revised")
    check("all_atomic", all(row["atomic_reading_de"] for row in ordered), "nonempty")
    check("all_decisions", all(row["decision"] for row in ordered), "nonempty")
    check("workshop_removed", all(row["decision"] == "REMOVE_FROM_WHOLE_CARD_DRAWER" for row in workshop), "57/57")
    check("cph_12", len(cph) == 12, len(cph))
    check("cph_11_surfaces", len({row["surface"] for row in cph}) == 11, len({row["surface"] for row in cph}))
    check("cph_four_registers", len({row["register"] for row in cph}) == 4, sorted({row["register"] for row in cph}))
    check("family_rows_7", len(families) == 7, len(families))
    check("family_unique", len({row["family"] for row in families}) == len(families), [row["family"] for row in families])
    check("same_surface_field", all(row["same_surface_other_codes"] for row in ordered), "NONE explicit")
    check("contexts_nonempty", all(row["local_contexts"] for row in ordered), "240/240")
    check("sealed_absent", all("f84" not in "\t".join(row.values()).lower() for row in ordered + workshop + cph), "f84/f84r absent")

    result = {
        "status": "PASS" if all(row["pass"] for row in checks) else "FAIL",
        "checks_passed": sum(bool(row["pass"]) for row in checks),
        "checks_total": len(checks),
        "checks": checks,
    }
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(1)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
