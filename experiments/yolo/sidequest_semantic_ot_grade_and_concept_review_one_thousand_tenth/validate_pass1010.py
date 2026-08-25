#!/usr/bin/env python3
"""Validate the Pass-1010 OT-grade release."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
P1009 = ROOT / "experiments/yolo/sidequest_semantic_twenty_two_page_statement_consolidation_one_thousand_ninth"
P1002 = ROOT / "experiments/yolo/sidequest_semantic_dual_layer_release_one_thousand_second"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def rightmost_grade(component_sequence: str) -> str:
    grades: list[str] = []
    for component in component_sequence.split(" | "):
        grades.extend(token for token in component.split("+") if token in {"E", "EE", "EEE"})
    return grades[-1] if grades else "NONE"


def expected_transition(source: str, target: str) -> str:
    rank = {"E": 1, "EE": 2, "EEE": 3}
    if source == "NONE":
        return "FIRST_ASSIGNED"
    if source == target:
        return "SAME"
    return "RAISED" if rank[target] > rank[source] else "LOWERED"


paths = {
    "chains": OUT / "PASS1010_24_OT_GRADE_CHAINS.tsv",
    "matrix": OUT / "PASS1010_OPERATION_GRADE_MATRIX.tsv",
    "grid": OUT / "PASS1010_GRADE_ENDPOINT_GRID.tsv",
    "codebook": OUT / "PASS1010_175_GRADE_REVISED_CODEBOOK.tsv",
    "statements": OUT / "PASS1010_627_GRADE_AWARE_STATEMENTS.tsv",
    "report": OUT / "PASS1010_OT_GRADE_REPORT.md",
    "summary": OUT / "PASS1010_BUILD_SUMMARY.json",
    "workshop_review": OUT / "CONCEPT_REVIEW_WORKSHOP_DESIGN.md",
    "historical_review": OUT / "CONCEPT_REVIEW_HISTORICAL_SEMANTIC.md",
    "synthesis": OUT / "PASS1010_CONCEPT_SYNTHESIS.md",
}
source_paths = {
    "statements": P1009 / "PASS1009_627_STATEMENT_EDITION.tsv",
    "events": P1009 / "PASS1009_4581_EVENT_LEDGER.tsv",
    "ellipses": P1009 / "PASS1009_27_ELLIPSIS_RESOLUTIONS.tsv",
    "codebook": P1002 / "PASS1002_175_CURRENT_CODEBOOK.tsv",
}

chains = read_tsv(paths["chains"])
matrix = read_tsv(paths["matrix"])
grid = read_tsv(paths["grid"])
new_codebook = read_tsv(paths["codebook"])
new_statements = read_tsv(paths["statements"])
old_statements = read_tsv(source_paths["statements"])
events = read_tsv(source_paths["events"])
old_ellipses = read_tsv(source_paths["ellipses"])
old_codebook = read_tsv(source_paths["codebook"])
summary = json.loads(paths["summary"].read_text(encoding="utf-8"))

checks: dict[str, bool] = {}
checks["24 action chains"] = len(chains) == 24
checks["8 operation rows"] = len(matrix) == 8
checks["6 grade endpoint cells"] = len(grid) == 6
checks["175 codebook rows"] = len(new_codebook) == 175
checks["627 statement rows"] = len(new_statements) == 627
checks["chain IDs unique"] = len({row["statement_id"] for row in chains}) == 24

old_action = {
    row["statement_id"]: row
    for row in old_ellipses
    if row["resolution_kind"] == "ANAPHORIC_ACTION_INHERITANCE"
}
old_statement_by_id = {row["statement_id"]: row for row in old_statements}
chain_by_id = {row["statement_id"]: row for row in chains}
checks["chain ID set exact"] = set(chain_by_id) == set(old_action)
checks["chain surface exact"] = all(
    chain_by_id[sid]["surface_sequence"] == old_action[sid]["surface_sequence"] for sid in old_action
)
checks["chain components exact"] = all(
    chain_by_id[sid]["component_sequence"] == old_action[sid]["component_sequence"] for sid in old_action
)
checks["operations exact"] = all(
    chain_by_id[sid]["inherited_operation_de"] == old_action[sid]["inherited_operation_de"]
    for sid in old_action
)
checks["sources exact"] = all(
    chain_by_id[sid]["source_statement_id"] == old_action[sid]["inheritance_source_statement_id"]
    for sid in old_action
)
checks["source earlier"] = all(
    int(chain_by_id[sid]["source_statement_id"].split("S")[-1]) < int(sid.split("S")[-1])
    for sid in chain_by_id
)
checks["same page inheritance"] = all(
    old_statement_by_id[row["source_statement_id"]]["physical_page"] == row["physical_page"]
    for row in chains
)
checks["same owner inheritance"] = all(
    old_statement_by_id[row["source_statement_id"]]["owner_id"] == row["owner_id"]
    for row in chains
)
checks["source grade exact"] = all(
    rightmost_grade(old_statement_by_id[row["source_statement_id"]]["component_sequence"])
    == row["source_rightmost_grade"]
    for row in chains
)
checks["transition exact"] = all(
    expected_transition(row["source_rightmost_grade"], row["target_grade"]) == row["grade_transition"]
    for row in chains
)
checks["transition counts exact"] = Counter(row["grade_transition"] for row in chains) == Counter(
    {"SAME": 13, "LOWERED": 6, "RAISED": 3, "FIRST_ASSIGNED": 2}
)
checks["grade values exact"] = {row["target_grade"] for row in chains} == {"E", "EE", "EEE"}
checks["atomic readings complete"] = all(
    row["inherited_operation_de"] in row["atomic_workshop_reading_de"]
    and row["target_grade"] in {"E", "EE", "EEE"}
    for row in chains
)

matrix_by_op = {row["inherited_operation_de"]: row for row in matrix}
expected_matrix = {
    "ABSETZEN": (0, 2, 0),
    "AUSWÄHLEN": (2, 0, 0),
    "GEBEN": (1, 0, 1),
    "LEITEN": (0, 1, 0),
    "NEHMEN": (1, 0, 0),
    "SETZEN": (9, 5, 0),
    "STELLEN": (0, 1, 0),
    "UMSETZEN": (1, 0, 0),
}
checks["operation set exact"] = set(matrix_by_op) == set(expected_matrix)
checks["operation matrix exact"] = all(
    tuple(int(matrix_by_op[op][field]) for field in ("grade_E_count", "grade_EE_count", "grade_EEE_count"))
    == counts
    for op, counts in expected_matrix.items()
)
checks["operation totals 24"] = sum(int(row["total"]) for row in matrix) == 24
checks["SETZEN has two grades"] = matrix_by_op["SETZEN"]["grade_contrast"] == "MULTIPLE_GRADES"
checks["GEBEN has two grades"] = matrix_by_op["GEBEN"]["grade_contrast"] == "MULTIPLE_GRADES"

expected_grid = {
    "OT+E+Y": (12, 1),
    "OT+E+DY": (29, 0),
    "OT+EE+Y": (23, 5),
    "OT+EE+DY": (26, 2),
    "OT+EEE+Y": (0, 0),
    "OT+EEE+DY": (1, 0),
}
grid_by_recipe = {row["component_recipe"]: row for row in grid}
checks["grid recipes exact"] = set(grid_by_recipe) == set(expected_grid)
checks["grid counts exact"] = all(
    (int(grid_by_recipe[recipe]["running_events"]), int(grid_by_recipe[recipe]["local_address_events"]))
    == counts
    for recipe, counts in expected_grid.items()
)
checks["grid recomputed from events"] = all(
    (
        sum(1 for row in events if row["component_recipe"] == recipe and row["event_role"] == "RUNNING_STATEMENT"),
        sum(1 for row in events if row["component_recipe"] == recipe and row["event_role"] == "LOCAL_ADDRESS_OR_LABEL"),
    )
    == counts
    for recipe, counts in expected_grid.items()
)
checks["E has open and closed cells"] = int(grid_by_recipe["OT+E+Y"]["running_events"]) > 0 and int(
    grid_by_recipe["OT+E+DY"]["running_events"]
) > 0
checks["EE has open and closed cells"] = int(grid_by_recipe["OT+EE+Y"]["running_events"]) > 0 and int(
    grid_by_recipe["OT+EE+DY"]["running_events"]
) > 0
checks["EEE singleton remains explicit"] = int(grid_by_recipe["OT+EEE+DY"]["total_events"]) == 1

checks["codebook identity preserved"] = [row["teaching_unit_id"] for row in new_codebook] == [
    row["teaching_unit_id"] for row in old_codebook
]
old_codebook_by_id = {row["teaching_unit_id"]: row for row in old_codebook}
new_codebook_by_id = {row["teaching_unit_id"]: row for row in new_codebook}
checks["root E revised"] = new_codebook_by_id["R-E"]["spoken_value_de"] == "GRAD I"
checks["root EE revised"] = new_codebook_by_id["R-EE"]["spoken_value_de"] == "GRAD II"
checks["root EEE revised"] = new_codebook_by_id["R-EEE"]["spoken_value_de"] == "GRAD III"
checks["non-grade codebook columns preserved"] = all(
    all(
        new_codebook_by_id[unit][field] == old_codebook_by_id[unit][field]
        for field in ("teaching_unit_id", "layer", "unit_type", "recognition_forms", "specialist_surface_forms", "observed_specialist_events", "pages")
    )
    for unit in old_codebook_by_id
)
checks["no old standalone grade words in spoken values"] = all(
    all(token not in {"KURZ", "LÄNGER", "VOLL"} for token in row["spoken_value_de"].split(" · "))
    for row in new_codebook
)

old_statement_fields = list(old_statements[0])
checks["statement IDs preserved"] = [row["statement_id"] for row in new_statements] == [
    row["statement_id"] for row in old_statements
]
checks["statement source columns preserved"] = all(
    all(new[field] == old[field] for field in old_statement_fields if field != "portable_literal_de")
    for new, old in zip(new_statements, old_statements)
)
checks["24 revised statement policies"] = sum(
    row["grade_policy"] == "INHERITED_OPERATION_PLUS_EXPLICIT_GRADE" for row in new_statements
) == 24
checks["603 unchanged policies"] = sum(
    row["grade_policy"] == "NO_PASS1010_ACTION_ELLIPSIS_REVISION" for row in new_statements
) == 603
checks["all statement grade readings complete"] = all(row["grade_neutral_workshop_de"] for row in new_statements)
checks["action chain neutral readings agree"] = all(
    next(row for row in new_statements if row["statement_id"] == chain["statement_id"])["grade_neutral_workshop_de"]
    == chain["grade_neutral_fluent_de"]
    for chain in chains
)

checks["summary status"] = summary["status"] == "PASS"
checks["summary decision"] = summary["decision"] == "OT_INHERITS_OPERATION_WHILE_E_EE_EEE_SET_AN_INDEPENDENT_WORK_GRADE"
checks["summary counts"] = summary["action_inheritance_chains"] == 24 and summary["codebook_rows"] == 175 and summary[
    "statement_rows"
] == 627
checks["zero new roots"] = summary["portable_roots"] == 53 and summary["new_portable_roots"] == 0
checks["source hashes exact"] = summary["source_hashes"] == {
    path.name: sha256(path) for path in source_paths.values()
}
checks["output hashes exact"] = summary["output_hashes"] == {
    paths[key].name: sha256(paths[key])
    for key in ("chains", "matrix", "grid", "codebook", "statements", "report")
}

report_text = paths["report"].read_text(encoding="utf-8")
checks["report core counts"] = all(fragment in report_text for fragment in ("**13**", "**6**", "**3**", "**2**"))
checks["report grade correction"] = all(fragment in report_text for fragment in ("E = GRAD I", "EE = GRAD II", "EEE = GRAD III"))
checks["report formula"] = "OT + GRAD + Y/DY" in report_text
checks["workshop concept review present"] = "Werkstattlehrmeisters um 1420" in paths[
    "workshop_review"
].read_text(encoding="utf-8")
checks["historical concept review present"] = "medizinisch-alchemistisches" in paths[
    "historical_review"
].read_text(encoding="utf-8")
checks["concept synthesis present"] = "53 gleich sichere" in paths["synthesis"].read_text(encoding="utf-8")

data_text = "\n".join(paths[key].read_text(encoding="utf-8") for key in ("chains", "matrix", "grid", "codebook", "statements", "report"))
checks["sealed folios absent from data"] = "f84" not in data_text.lower()
checks["absolute workspace path absent"] = str(ROOT) not in data_text

tracked_outputs = [paths[key] for key in ("chains", "matrix", "grid", "codebook", "statements", "report", "summary")]
before = {path.name: sha256(path) for path in tracked_outputs}
subprocess.run(["python3", str(OUT / "build_pass1010.py")], cwd=ROOT, check=True, capture_output=True, text=True)
after = {path.name: sha256(path) for path in tracked_outputs}
checks["deterministic rebuild byte-identical"] = before == after

failed = [name for name, passed in checks.items() if not passed]
result = {
    "status": "PASS" if not failed else "FAIL",
    "checks_total": len(checks),
    "checks_passed": len(checks) - len(failed),
    "checks_failed": failed,
    "counts": {
        "action_chains": len(chains),
        "operations": len(matrix),
        "grid_cells": len(grid),
        "codebook_rows": len(new_codebook),
        "statements": len(new_statements),
    },
    "checks": checks,
}
(OUT / "PASS1010_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
if failed:
    print(f"FAIL: {len(failed)} / {len(checks)} checks")
    for name in failed:
        print(name)
    raise SystemExit(1)
print(f"PASS: {len(checks)}/{len(checks)} checks")
