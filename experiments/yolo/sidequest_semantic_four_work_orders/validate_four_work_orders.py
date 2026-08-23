#!/usr/bin/env python3
"""Validate the four creative execution-order work orders."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
READER = ROOT / "experiments/yolo/sidequest_semantic_ten_page_unified_reader"
PHASE_RANK = {"WHEN": 0, "WHAT": 1, "HOW": 2}
EXPECTED_ORDER_COUNTS = {
    "D1_ROOT_BATH_RIGHT_WHEEL": 173,
    "D2_CLEAR_EXTRACT_STAR_ATLAS": 144,
    "D3_STORED_APPLICATION_THREE_WHEELS": 225,
    "D4_FRESH_PLANT_LEFT_WHEEL": 234,
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    checks: list[dict[str, object]] = []

    def check(name: str, condition: bool, detail: object) -> None:
        checks.append({"check": name, "pass": bool(condition), "detail": detail})

    orders = read_tsv(OUT / "FOUR_WORK_ORDERS.tsv")
    steps = read_tsv(OUT / "TWENTY_FIVE_EXECUTION_STEPS.tsv")
    units = read_tsv(OUT / "FOUR_WORK_ORDER_258_UNITS.tsv")
    trace = read_tsv(OUT / "TEN_PAGE_776_WORK_ORDER_TRACE.tsv")
    source_trace = read_tsv(READER / "TEN_PAGE_776_READER_TRACE.tsv")
    source_units = read_tsv(READER / "TEN_PAGE_258_READING_UNITS.tsv")

    check("four_work_orders", len(orders) == 4, len(orders))
    check("twenty_five_steps", len(steps) == 25, len(steps))
    check("258_reading_units", len(units) == 258, len(units))
    check("776_visible_groups", len(trace) == 776, len(trace))

    unit_kinds = Counter(row["unit_kind"] for row in units)
    registers = Counter(row["register"] for row in trace)
    check("116_prose_statements", unit_kinds["PROSE_STATEMENT"] == 116, unit_kinds)
    check("142_astro_loci", unit_kinds["ASTRO_VISIBLE_LOCUS"] == 142, unit_kinds)
    check("381_prose_groups", registers["PROSE"] == 381, registers)
    check("395_astro_groups", registers["ASTRO"] == 395, registers)

    ids = [row["work_order_id"] for row in orders]
    check("work_order_ids_exact", set(ids) == set(EXPECTED_ORDER_COUNTS), ids)
    check("execution_order_fixed", all(row["execution_order"] == "WHEN>WHAT>HOW" for row in orders), "all")
    actual_counts = Counter(row["work_order_id"] for row in trace)
    check("work_order_group_counts", dict(actual_counts) == EXPECTED_ORDER_COUNTS, dict(actual_counts))
    check(
        "summary_group_counts_match",
        all(int(row["total_groups"]) == EXPECTED_ORDER_COUNTS[row["work_order_id"]] for row in orders),
        {row["work_order_id"]: row["total_groups"] for row in orders},
    )
    check("group_counts_sum", sum(int(row["total_groups"]) for row in orders) == 776, "776")
    check("unit_counts_sum", sum(int(row["total_reading_units"]) for row in orders) == 258, "258")

    # Each dossier must execute all WHEN steps, then WHAT, then HOW, without a
    # return to an earlier phase.
    phase_sequences: dict[str, list[str]] = {}
    step_numbers_ok = True
    for did in ids:
        local = sorted((row for row in steps if row["work_order_id"] == did), key=lambda row: int(row["execution_step"]))
        phases = [row["phase"] for row in local]
        phase_sequences[did] = phases
        step_numbers_ok &= [int(row["execution_step"]) for row in local] == list(range(1, len(local) + 1))
    check("step_numbers_continuous", step_numbers_ok, "all four")
    check(
        "phase_order_when_what_how",
        all(
            [PHASE_RANK[phase] for phase in phases] == sorted(PHASE_RANK[phase] for phase in phases)
            and set(phases) == {"WHEN", "WHAT", "HOW"}
            for phases in phase_sequences.values()
        ),
        phase_sequences,
    )

    # Execution unit numbering is local to the work order and all unit rows
    # inherit the phase/source-unit assignment of their step.
    unit_numbering_ok = True
    step_phase = {(row["work_order_id"], row["source_unit"]): (row["phase"], row["execution_step"]) for row in steps}
    unit_assignment_ok = True
    for did in ids:
        local = [row for row in units if row["work_order_id"] == did]
        unit_numbering_ok &= [int(row["execution_unit_no"]) for row in local] == list(range(1, len(local) + 1))
        for row in local:
            expected = step_phase[(did, row["source_unit"])]
            unit_assignment_ok &= (row["phase"], row["execution_step"]) == expected
    check("execution_unit_numbers_continuous", unit_numbering_ok, "all four")
    check("unit_step_assignment_consistent", unit_assignment_ok, "all")

    source_by_group = {row["source_group_id"]: row for row in source_trace}
    output_by_group = {row["source_group_id"]: row for row in trace}
    check("source_groups_unique", len(source_by_group) == 776, len(source_by_group))
    check("output_groups_unique", len(output_by_group) == 776, len(output_by_group))
    check("source_group_set_exact", set(source_by_group) == set(output_by_group), "exact")
    exact_group_copy = True
    for group_id, source in source_by_group.items():
        output = output_by_group[group_id]
        for field in (
            "register", "page", "reading_unit_id", "visible_owner", "visible_surface", "lookup_id",
            "resolved_entry_id", "resolved_reading_de", "lookup_status",
        ):
            exact_group_copy &= source[field] == output[field]
    check("current_group_readings_preserved", exact_group_copy, "all copied fields exact")
    check(
        "work_order_serials_continuous",
        [row["work_order_serial"] for row in trace] == [f"W{index:03d}" for index in range(1, 777)],
        "W001-W776",
    )

    source_unit_by_key = {
        ("PROSE" if row["unit_kind"] == "PROSE_STATEMENT" else "ASTRO", row["unit_id"]): row
        for row in source_units
    }
    output_unit_by_key = {
        ("PROSE" if row["unit_kind"] == "PROSE_STATEMENT" else "ASTRO", row["unit_id"]): row
        for row in units
    }
    check("source_units_unique", len(source_unit_by_key) == 258, len(source_unit_by_key))
    check("output_units_unique", len(output_unit_by_key) == 258, len(output_unit_by_key))
    check("source_unit_set_exact", set(source_unit_by_key) == set(output_unit_by_key), "exact")
    exact_unit_copy = True
    for key, source in source_unit_by_key.items():
        output = output_unit_by_key[key]
        for field in (
            "unit_kind", "page", "record_or_diagram", "visible_owner", "visible_surface_sequence",
            "lookup_sequence", "literal_reading_sequence_de", "fluent_workshop_reading_de", "reading_rule",
        ):
            exact_unit_copy &= source[field] == output[field]
    check("current_unit_readings_preserved", exact_unit_copy, "all copied fields exact")

    groups_by_unit = Counter((row["work_order_id"], row["reading_unit_id"]) for row in trace)
    units_without_groups = [
        (row["work_order_id"], row["unit_id"])
        for row in units
        if groups_by_unit[(row["work_order_id"], row["unit_id"])] == 0
    ]
    check("every_reading_unit_has_groups", not units_without_groups, units_without_groups[:5])

    expected_pages = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r", "f67r2", "f68r1", "f69v"}
    check("ten_pages_exact", {row["page"] for row in trace} == expected_pages, sorted({row["page"] for row in trace}))
    check(
        "assignment_status_fixed",
        all(row["assignment_status"] == "CREATIVE_WORK_ORDER_PAIRING__CURRENT_READER_VALUE" for row in trace),
        "all",
    )

    cards = (OUT / "FOUR_ONE_PAGE_JOB_CARDS.md").read_text(encoding="utf-8")
    complete = (OUT / "FOUR_COMPLETE_WORK_ORDERS.md").read_text(encoding="utf-8")
    report = (OUT / "FOUR_WORK_ORDER_REPORT.md").read_text(encoding="utf-8")
    check("job_cards_show_execution_order", "WANN wählen → WAS bereitstellen → WIE ausführen" in cards, "present")
    check("all_orders_in_job_cards", all(f"## {did}" in cards for did in ids), "all")
    check("all_units_in_complete_book", all(f"**{row['unit_id']}**" in complete for row in units), "all")
    check("report_marks_creative_pairing", "kreative Werkstattordnung" in report, "present")
    check("report_rejects_hidden_diagram_key", "unsichtbaren gemeinsamen Schlüssel" in report, "present")

    content_names = [
        "FOUR_WORK_ORDERS.tsv", "TWENTY_FIVE_EXECUTION_STEPS.tsv", "FOUR_WORK_ORDER_258_UNITS.tsv",
        "TEN_PAGE_776_WORK_ORDER_TRACE.tsv", "FOUR_ONE_PAGE_JOB_CARDS.md",
        "FOUR_COMPLETE_WORK_ORDERS.md", "FOUR_WORK_ORDER_REPORT.md",
    ]
    content = "\n".join((OUT / name).read_text(encoding="utf-8", errors="replace") for name in content_names)
    sealed_pattern = re.compile(r"(?i)(?<![a-z0-9])f84(?:r|v)?(?![a-z0-9])")
    check("sealed_pages_absent", sealed_pattern.search(content) is None, "absent")

    before = {name: digest(OUT / name) for name in content_names}
    subprocess.run([sys.executable, str(OUT / "build_four_work_orders.py")], cwd=ROOT, check=True, stdout=subprocess.DEVNULL)
    after = {name: digest(OUT / name) for name in content_names}
    check("deterministic_rebuild", before == after, "byte identical")

    passed = all(bool(row["pass"]) for row in checks)
    result = {
        "status": "PASS" if passed else "FAIL",
        "checks_passed": sum(bool(row["pass"]) for row in checks),
        "checks_total": len(checks),
        "checks": checks,
        "counts": {
            "work_orders": len(orders),
            "execution_steps": len(steps),
            "reading_units": len(units),
            "prose_statements": unit_kinds["PROSE_STATEMENT"],
            "astro_loci": unit_kinds["ASTRO_VISIBLE_LOCUS"],
            "visible_groups": len(trace),
            "prose_groups": registers["PROSE"],
            "astro_groups": registers["ASTRO"],
            "work_order_group_counts": dict(actual_counts),
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
