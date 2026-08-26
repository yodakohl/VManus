#!/usr/bin/env python3
"""Validate and deterministically rebuild the Pass-1025 register replay."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path


OUT = Path(__file__).resolve().parent


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    events = read_tsv(OUT / "PASS1025_3888_REGISTER_EVENT_REPLAY.tsv")
    attachments = read_tsv(OUT / "PASS1025_4342_CORRECTED_ATTACHMENTS.tsv")
    corrections = read_tsv(OUT / "PASS1025_SURFACE_DETERMINISM_CORRECTIONS.tsv")
    statements = read_tsv(OUT / "PASS1025_EIGHT_CORRECTED_STATEMENTS.tsv")
    categories = read_tsv(OUT / "PASS1025_31_CATEGORY_REGISTER_SUPPORT.tsv")
    rules = read_tsv(OUT / "PASS1025_9_RULE_REGISTER_SUPPORT.tsv")
    micros = read_tsv(OUT / "PASS1025_MICROFORM_REGISTER_SUPPORT.tsv")
    registers = read_tsv(OUT / "PASS1025_FOUR_REGISTER_REPLAY.tsv")

    checks: dict[str, bool] = {}
    checks["inventory_counts"] = [len(events), len(attachments), len(corrections), len(statements), len(categories), len(rules), len(registers)] == [3888, 4342, 18, 8, 31, 9, 4]
    checks["unique_event_ids"] = len({row["event_id"] for row in events}) == 3888
    checks["four_registers"] = {row["held_register"] for row in registers} == {"HERBAL", "BIOLOGICAL", "CELESTIAL", "PHARMA"}
    checks["event_register_partition"] = Counter(row["held_register"] for row in events) == Counter(
        {"HERBAL": 601, "BIOLOGICAL": 2161, "CELESTIAL": 523, "PHARMA": 603}
    )
    checks["event_result_partition"] = Counter(row["register_replay_result"] for row in events) == Counter(
        {
            "EXACT_SURFACE_FROM_OTHER_REGISTER": 2261,
            "ROOT_RECIPE_FROM_OTHER_REGISTER": 594,
            "NEW_REGISTER_RECIPE__KNOWN_ATOMS": 1033,
        }
    )
    checks["all_event_atoms_fixed"] = all(row["all_atoms_on_fixed_sheet"] == "YES" for row in events)
    surface_recipes: dict[str, set[str]] = {}
    for row in events:
        surface_recipes.setdefault(row["surface"], set()).add(row["component_recipe"])
    checks["one_visible_surface_one_recipe"] = all(len(recipes) == 1 for recipes in surface_recipes.values())
    checks["two_surface_repairs"] = (
        {row["surface"] for row in events if row["surface_recipe_correction"] != "UNCHANGED"} == {"cheo", "okeor"}
        and sum(row["surface_recipe_correction"] != "UNCHANGED" for row in events) == 9
        and {row["component_recipe"] for row in events if row["surface"] == "cheo"} == {"CH+E+O"}
        and {row["component_recipe"] for row in events if row["surface"] == "okeor"} == {"OK+E+OR"}
    )
    checks["attachment_repairs"] = (
        not any(row["surface_card"] == "cheo" and row["focus_core"] in {"L", "R"} for row in attachments)
        and not any(row["surface_card"] == "okeor" and row["focus_core"] == "EE" for row in attachments)
        and sum(row["surface_card"] == "okeor" and row["focus_core"] == "E" for row in attachments) == 3
        and all(
            "R_POSITIONAL_MARKING" not in row["teaching_rule_families"]
            for row in attachments
            if row["source_attachment_id"] in {"SA01107", "SA01108"}
        )
    )
    checks["eight_statement_revisions"] = (
        {row["statement_id"] for row in statements}
        == {"P1009-S019", "P1009-S056", "P1009-S057", "P1009-S067", "P1009-S244", "P1009-S254", "P1009-S617", "P1009-S627"}
        and sum(len(row["corrected_event_ids"].split("|")) for row in statements) == 9
    )
    checks["thirty_categories_universal"] = sum(int(row["support_register_count"]) == 4 for row in categories) == 30
    checks["vorbezug_two_registers"] = [
        (row["category_id"], row["support_registers"])
        for row in categories
        if int(row["support_register_count"]) < 4
    ] == [("CHANNEL_04", "HERBAL|CELESTIAL")]
    checks["all_used_categories_transfer"] = all(row["survives_every_register_where_used"] == "YES" for row in categories)
    checks["all_used_rules_transfer"] = all(row["survives_every_register_where_used"] == "YES" for row in rules)
    checks["all_registers_pass"] = all(row["register_replay_result"] == "PASS_FIXED_SHEET_AND_SCOPE" for row in registers)
    checks["no_unsupported_register_items"] = all(
        row["unsupported_category_holdouts"] == "NONE" and row["unsupported_rule_family_holdouts"] == "NONE"
        for row in registers
    )
    checks["four_private_microforms"] = {
        row["micro_signature"]
        for row in micros
        if row["register_private_microform"] == "YES"
    } == {"AL_AR_RIGHT_FALLBACK_NO_LEFT", "EQUAL_LEFT+R_HEAD", "EQUAL_RIGHT", "R_NESTED"}
    checks["private_micro_parents_transfer"] = all(
        row["all_parent_rules_cross_register"] == "YES"
        for row in micros
        if row["register_private_microform"] == "YES"
    )

    outputs = [
        OUT / "PASS1025_3888_REGISTER_EVENT_REPLAY.tsv",
        OUT / "PASS1025_4342_CORRECTED_ATTACHMENTS.tsv",
        OUT / "PASS1025_SURFACE_DETERMINISM_CORRECTIONS.tsv",
        OUT / "PASS1025_EIGHT_CORRECTED_STATEMENTS.tsv",
        OUT / "PASS1025_31_CATEGORY_REGISTER_SUPPORT.tsv",
        OUT / "PASS1025_9_RULE_REGISTER_SUPPORT.tsv",
        OUT / "PASS1025_MICROFORM_REGISTER_SUPPORT.tsv",
        OUT / "PASS1025_FOUR_REGISTER_REPLAY.tsv",
        OUT / "PASS1025_BUILD_SUMMARY.json",
    ]
    before = {path.name: sha(path) for path in outputs}
    subprocess.run([sys.executable, str(OUT / "build_pass1025.py")], check=True)
    after = {path.name: sha(path) for path in outputs}
    checks["deterministic_rebuild"] = before == after

    failed = [name for name, value in checks.items() if not value]
    result = {
        "result": "PASS" if not failed else "FAIL",
        "check_count": len(checks),
        "failed_checks": failed,
        "checks": checks,
        "output_hashes": after,
    }
    (OUT / "PASS1025_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if failed:
        raise SystemExit("failed: " + ", ".join(failed))


if __name__ == "__main__":
    main()
