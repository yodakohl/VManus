#!/usr/bin/env python3
"""Validate the creative menu-to-selected-path edition."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
SOURCE = ROOT / "experiments/yolo/sidequest_semantic_four_work_orders"

EXPECTED_SELECTED_GROUPS = {
    "A1:G018", "A1:G033", "A1:G034", "A1:G035", "A1:G148", "A1:G184",
    "A2:G013", "A2:G053", "A2:G065",
    "A3:G131", "A3:G132", "A3:G053", "A3:G097",
    "A1:G081", "A1:G082", "A1:G083", "A1:G137", "A1:G138", "A1:G139",
    "A1:G156", "A1:G166",
}
EXPECTED_ACTIVE_GROUPS = {
    "D1_ROOT_BATH_RIGHT_WHEEL": 110,
    "D2_CLEAR_EXTRACT_STAR_ATLAS": 82,
    "D3_STORED_APPLICATION_THREE_WHEELS": 89,
    "D4_FRESH_PLANT_LEFT_WHEEL": 121,
}
EXPECTED_ACTIVE_UNITS = {
    "D1_ROOT_BATH_RIGHT_WHEEL": 30,
    "D2_CLEAR_EXTRACT_STAR_ATLAS": 29,
    "D3_STORED_APPLICATION_THREE_WHEELS": 27,
    "D4_FRESH_PLANT_LEFT_WHEEL": 43,
}
PHASE_RANK = {"WHEN": 0, "WHAT": 1, "HOW": 2}


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    checks: list[dict[str, object]] = []

    def check(name: str, condition: bool, detail: object) -> None:
        checks.append({"check": name, "pass": bool(condition), "detail": detail})

    choices = rows(OUT / "SELECTED_13_ASTRO_CHOICES.tsv")
    menu = rows(OUT / "ASTRO_395_MENU_STATUS.tsv")
    echoes = rows(OUT / "SELECTED_9_CROSS_REGISTER_ECHOS.tsv")
    active_units = rows(OUT / "FOUR_ACTIVE_129_READING_STEPS.tsv")
    active_trace = rows(OUT / "FOUR_ACTIVE_402_GROUP_TRACE.tsv")
    paths = rows(OUT / "FOUR_SELECTED_JOB_PATHS.tsv")
    source_trace = rows(SOURCE / "TEN_PAGE_776_WORK_ORDER_TRACE.tsv")
    source_units = rows(SOURCE / "FOUR_WORK_ORDER_258_UNITS.tsv")

    check("four_selected_paths", len(paths) == 4, len(paths))
    check("thirteen_astro_choices", len(choices) == 13, len(choices))
    check("395_astro_menu_groups", len(menu) == 395, len(menu))
    check("nine_selected_cross_register_echoes", len(echoes) == 9, len(echoes))
    check(
        "echo_surfaces_exact",
        {row["visible_surface"] for row in echoes} == {"aiin", "cheey", "cho", "dal", "dy", "okeey", "okey", "oldy", "sheey"},
        sorted(row["visible_surface"] for row in echoes),
    )
    check("echo_nuclei_concrete", all(row["shared_workshop_nucleus_de"].strip() for row in echoes), "all")
    check("129_active_reading_steps", len(active_units) == 129, len(active_units))
    check("402_active_groups", len(active_trace) == 402, len(active_trace))

    menu_status = Counter(row["menu_status"] for row in menu)
    check("21_selected_astro_groups", menu_status["SELECTED_FOR_SAMPLE_JOB"] == 21, menu_status)
    check("374_unselected_menu_groups", menu_status["UNSELECTED_REFERENCE_OPTION"] == 374, menu_status)
    selected_menu_ids = {row["source_group_id"] for row in menu if row["menu_status"] == "SELECTED_FOR_SAMPLE_JOB"}
    check("selected_group_manifest_exact", selected_menu_ids == EXPECTED_SELECTED_GROUPS, sorted(selected_menu_ids))
    check("menu_group_ids_unique", len({row["source_group_id"] for row in menu}) == 395, "unique")

    unit_kind = Counter(row["unit_kind"] for row in active_units)
    role_counts = Counter(row["path_role"] for row in active_trace)
    check("116_prose_statements", unit_kind["PROSE_STATEMENT"] == 116, unit_kind)
    check("13_selected_astro_steps", unit_kind["SELECTED_ASTRO_OPTION"] == 13, unit_kind)
    check("381_executed_prose_groups", role_counts["EXECUTED_PROSE_CARD"] == 381, role_counts)
    check("21_selected_lookup_groups", role_counts["SELECTED_LOOKUP_VALUE"] == 21, role_counts)

    active_groups_by_order = Counter(row["work_order_id"] for row in active_trace)
    active_units_by_order = Counter(row["work_order_id"] for row in active_units)
    check("active_groups_by_work_order", dict(active_groups_by_order) == EXPECTED_ACTIVE_GROUPS, dict(active_groups_by_order))
    check("active_units_by_work_order", dict(active_units_by_order) == EXPECTED_ACTIVE_UNITS, dict(active_units_by_order))
    check("summary_active_group_counts", all(int(row["active_group_count"]) == EXPECTED_ACTIVE_GROUPS[row["work_order_id"]] for row in paths), "all")
    check("summary_active_unit_counts", all(int(row["active_reading_step_count"]) == EXPECTED_ACTIVE_UNITS[row["work_order_id"]] for row in paths), "all")

    source_by_group = {row["source_group_id"]: row for row in source_trace}
    active_by_group = {row["source_group_id"]: row for row in active_trace}
    check("source_trace_unique", len(source_by_group) == 776, len(source_by_group))
    check("active_trace_unique", len(active_by_group) == 402, len(active_by_group))
    source_prose_ids = {row["source_group_id"] for row in source_trace if row["register"] == "PROSE"}
    active_prose_ids = {row["source_group_id"] for row in active_trace if row["path_role"] == "EXECUTED_PROSE_CARD"}
    active_astro_ids = {row["source_group_id"] for row in active_trace if row["path_role"] == "SELECTED_LOOKUP_VALUE"}
    check("all_prose_groups_active", active_prose_ids == source_prose_ids, "381 exact")
    check("only_selected_astro_groups_active", active_astro_ids == EXPECTED_SELECTED_GROUPS, sorted(active_astro_ids))
    check("active_group_set_exact", set(active_by_group) == source_prose_ids | EXPECTED_SELECTED_GROUPS, "402 exact")

    exact_copy = True
    for group_id, active in active_by_group.items():
        source = source_by_group[group_id]
        for field in (
            "work_order_id", "page", "source_unit", "reading_unit_id", "visible_owner",
            "visible_surface", "lookup_id", "resolved_entry_id", "resolved_reading_de",
        ):
            exact_copy &= active[field] == source[field]
    check("active_group_values_preserved", exact_copy, "all copied fields exact")
    check(
        "active_group_serials_continuous",
        [row["active_group_serial"] for row in active_trace] == [f"P{index:03d}" for index in range(1, 403)],
        "P001-P402",
    )

    # Every original prose statement appears once and keeps its fluent value.
    source_prose_units = {
        (row["work_order_id"], row["unit_id"]): row
        for row in source_units
        if row["unit_kind"] == "PROSE_STATEMENT"
    }
    active_prose_units = {
        (row["work_order_id"], row["active_unit_id"]): row
        for row in active_units
        if row["unit_kind"] == "PROSE_STATEMENT"
    }
    check("prose_statement_set_exact", set(active_prose_units) == set(source_prose_units), "116 exact")
    check(
        "prose_statement_readings_preserved",
        all(
            active_prose_units[key]["fluent_workshop_reading_de"] == source["fluent_workshop_reading_de"]
            and active_prose_units[key]["literal_reading_sequence_de"] == source["literal_reading_sequence_de"]
            and active_prose_units[key]["visible_surface_sequence"] == source["visible_surface_sequence"]
            for key, source in source_prose_units.items()
        ),
        "all",
    )

    order_ids = [row["work_order_id"] for row in paths]
    numbering_ok = True
    phase_order_ok = True
    for did in order_ids:
        local = [row for row in active_units if row["work_order_id"] == did]
        numbering_ok &= [int(row["active_unit_no"]) for row in local] == list(range(1, len(local) + 1))
        ranks = [PHASE_RANK[row["phase"]] for row in local]
        phase_order_ok &= ranks == sorted(ranks) and set(row["phase"] for row in local) == {"WHEN", "WHAT", "HOW"}
    check("local_active_unit_numbering", numbering_ok, "all four")
    check("selected_when_what_how_order", phase_order_ok, "all four")
    check(
        "active_global_numbering",
        [int(row["active_global_no"]) for row in active_units] == list(range(1, 130)),
        "1-129",
    )
    check("all_condition_strings_concrete", all(row["selected_condition_de"].strip() for row in paths), "all")
    check("ten_pages_remain_active", {row["page"] for row in active_trace} == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r", "f67r2", "f68r1", "f69v"}, sorted({row["page"] for row in active_trace}))

    sheets = (OUT / "FOUR_FLUENT_SELECTED_JOB_SHEETS.md").read_text(encoding="utf-8")
    report = (OUT / "MENU_TO_PATH_REPORT.md").read_text(encoding="utf-8")
    check("all_paths_in_readable_sheets", all(f"## {did}" in sheets for did in order_ids), "all")
    check("all_active_units_in_readable_sheets", all(f"**{row['active_unit_id']}**" in sheets for row in active_units), "all")
    check("report_menu_correction_present", "Ein Rad mit 28 Plätzen ist jedoch ein Menü" in report, "present")
    check("report_no_hidden_cross_diagram_key", "verborgenen Schlüssel zwischen den Diagrammseiten" in report, "present")
    check("report_nine_card_dictionary_gain", "Neun ausgewählte Diagrammkarten" in report, "present")

    content_names = [
        "SELECTED_13_ASTRO_CHOICES.tsv", "ASTRO_395_MENU_STATUS.tsv",
        "SELECTED_9_CROSS_REGISTER_ECHOS.tsv",
        "FOUR_ACTIVE_129_READING_STEPS.tsv", "FOUR_ACTIVE_402_GROUP_TRACE.tsv",
        "FOUR_SELECTED_JOB_PATHS.tsv", "FOUR_FLUENT_SELECTED_JOB_SHEETS.md",
        "MENU_TO_PATH_REPORT.md",
    ]
    content = "\n".join((OUT / name).read_text(encoding="utf-8", errors="replace") for name in content_names)
    sealed_pattern = re.compile(r"(?i)(?<![a-z0-9])f84(?:r|v)?(?![a-z0-9])")
    check("sealed_pages_absent", sealed_pattern.search(content) is None, "absent")

    before = {name: digest(OUT / name) for name in content_names}
    subprocess.run([sys.executable, str(OUT / "build_selected_job_paths.py")], cwd=ROOT, check=True, stdout=subprocess.DEVNULL)
    after = {name: digest(OUT / name) for name in content_names}
    check("deterministic_rebuild", before == after, "byte identical")

    passed = all(bool(row["pass"]) for row in checks)
    result = {
        "status": "PASS" if passed else "FAIL",
        "checks_passed": sum(bool(row["pass"]) for row in checks),
        "checks_total": len(checks),
        "checks": checks,
        "counts": {
            "work_orders": len(paths),
            "astro_choices": len(choices),
            "selected_cross_register_echoes": len(echoes),
            "selected_astro_groups": len(selected_menu_ids),
            "unselected_astro_menu_groups": menu_status["UNSELECTED_REFERENCE_OPTION"],
            "active_reading_steps": len(active_units),
            "active_prose_statements": unit_kind["PROSE_STATEMENT"],
            "active_groups": len(active_trace),
            "active_prose_groups": role_counts["EXECUTED_PROSE_CARD"],
            "active_astro_groups": role_counts["SELECTED_LOOKUP_VALUE"],
            "active_groups_by_work_order": dict(active_groups_by_order),
        },
    }
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if not passed:
        for row in checks:
            if not row["pass"]:
                print(f"FAIL {row['check']}: {row['detail']}")
        raise SystemExit(1)
    print(f"PASS {result['checks_passed']}/{result['checks_total']}")


if __name__ == "__main__":
    main()
