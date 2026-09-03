#!/usr/bin/env python3
"""Independent source, score, safety, and byte-replay checks for GDT772."""

from __future__ import annotations

import argparse
import ast
import copy
import csv
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Mapping, Sequence


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt772_expanded_ol_branch_masked_rescore"
SRC = EXP / "src"
ART = EXP / "artifacts"
RUN = SRC / "run.py"
VALIDATION = ART / "VALIDATION.json"
G770 = ROOT / "experiments/yolo/gdt770_target_masked_valency_orphan_tournament"
OLD_COHORT = G770 / "src/COHORT_15_LINE_SPECS.tsv"
OLD_SLOTS = G770 / "src/TARGET_INDEPENDENT_SLOT_CONSTRAINTS.tsv"
CANDIDATES = G770 / "src/CANDIDATE_POLICY_SPECS.tsv"
PENALTIES = G770 / "src/PENALTY_SPECS.tsv"
G734_CELLS = ROOT / "experiments/yolo/gdt734_v99r7_recurrent_unknown_family_dispatch/artifacts/V99R7_32339_COMPACT_CELL_REGISTER.tsv"
NEW_LINES = SRC / "NEW_LINE_SPECS.tsv"
NEW_EDGES = SRC / "NEW_EDGE_ROLE_SPECS.tsv"
OVERRIDES = SRC / "RERENDER_OVERRIDE_SPECS.tsv"
MANUAL_READINGS = SRC / "MANUAL_RECIPE_READING_SPECS.tsv"
LOCK = SRC / "SCORE_CONTRACT_LOCK.tsv"
COHORT_ART = ART / "EXPANDED_22_LINE_COHORT.tsv"
POLICY_ART = ART / "TARGET_POLICY_SCOREBOARD.tsv"
DECISION_ART = ART / "TARGET_DECISIONS.tsv"
CASES_ART = ART / "OL_POSITIONAL_VS_NOMINAL_CASES.tsv"
RESULT_ART = ART / "RESULT.json"
TARGET_MASKS = {"ol": "TM-Q7M2", "ckhy": "TM-V4C9", "ols": "TM-H8R1", "otar": "TM-N5K6"}
EXPECTED_OL = {
    "OL_NULL": 127,
    "OL_POSITIONAL_RELATOR": 56,
    "OL_NOMINAL_BASE": 56,
    "OL_MEASURABLE_PRODUCT_RESULT": 76,
}
CELL_COLUMNS = (
    "cell_id", "page", "locus", "token_ordinal", "surface",
    "v99r7_semantic_value_de", "v99r7_spoken_cell_de", "gdt734_confidence_level",
    "gdt734_semantic_scope", "practical_unit_layer", "practical_unit_id",
    "practical_unit_role", "v99r7_practical_render_once_de", "unknown_v99r7",
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def literal_outputs() -> tuple[str, ...]:
    tree = ast.parse(RUN.read_text(encoding="utf-8"))
    assignments = [node for node in tree.body if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == "OUTPUT_NAMES" for target in node.targets)]
    if len(assignments) != 1:
        raise AssertionError("runner must contain one literal OUTPUT_NAMES assignment")
    value = ast.literal_eval(assignments[0].value)
    if not isinstance(value, tuple) or not all(isinstance(item, str) for item in value):
        raise AssertionError("OUTPUT_NAMES is not a literal tuple")
    return value


def import_independent_scorer():
    path = G770 / "src/validate.py"
    spec = importlib.util.spec_from_file_location("gdt770_independent_validator", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load frozen independent score implementation")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def guarded_cells(line_specs: Sequence[Mapping[str, str]]) -> tuple[list[dict[str, str]], dict[str, int]]:
    loci = [row["locus"] for row in line_specs]
    if len(loci) != 7 or len(set(loci)) != 7 or any(re.match(r"^f84(?:r|v|$)", locus) for locus in loci):
        raise AssertionError("unsafe or malformed new-line allow list")
    command = [str(ROOT / "vmanus-exp"), "query-tsv", str(G734_CELLS.relative_to(ROOT)), "--selector", "locus"]
    for locus in loci:
        command.extend(("--allow", locus))
    command.extend(("--columns", ",".join(CELL_COLUMNS)))
    completed = subprocess.run(command, cwd=ROOT, check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    rows = list(csv.DictReader(completed.stdout.splitlines(), delimiter="\t"))
    stats_lines = [line for line in completed.stderr.splitlines() if line.startswith("GUARD_STATS ")]
    if len(stats_lines) != 1:
        raise AssertionError("guard statistics missing")
    return rows, json.loads(stats_lines[0].removeprefix("GUARD_STATS "))


def score_totals(core: Mapping[str, object]) -> dict[str, int]:
    return {candidate_id: int(summary["total_penalty"]) for candidate_id, summary in core["summaries"].items()}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifacts-dir", type=Path, default=ART)
    parser.add_argument("--validation-path", type=Path, default=VALIDATION)
    args = parser.parse_args()
    artifacts = args.artifacts_dir if args.artifacts_dir.is_absolute() else ROOT / args.artifacts_dir
    validation_path = args.validation_path if args.validation_path.is_absolute() else ROOT / args.validation_path
    checks = 0
    failures: list[str] = []

    def check(condition: bool, message: str) -> None:
        nonlocal checks
        checks += 1
        if not condition:
            failures.append(message)

    outputs = literal_outputs()
    check(len(outputs) == 14 and len(set(outputs)) == 14, "runner output contract changed")
    check(all((artifacts / name).is_file() for name in outputs), "declared runner artifact missing")
    locks = read_tsv(LOCK)
    check(len(locks) == 11, "contract-lock row count changed")
    for row in locks:
        path = Path(row["path"])
        check(not path.is_absolute() and ".." not in path.parts, f"unsafe locked path: {path}")
        check(sha256(ROOT / path) == row["expected_sha256"], f"locked input hash changed: {path}")

    line_specs, edge_specs, overrides = read_tsv(NEW_LINES), read_tsv(NEW_EDGES), read_tsv(OVERRIDES)
    manual_readings = read_tsv(MANUAL_READINGS)
    queried, guard_stats = guarded_cells(line_specs)
    check(guard_stats == {"selected": 55, "skipped_forbidden": 0, "skipped_not_allowed": 32284}, "guard statistics changed")
    check(len(queried) == 55 and not any(row["page"].startswith("f84") for row in queried), "guard selected unsafe or wrong rows")
    by_locus: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
    for row in queried:
        by_locus[row["locus"]].append(row)
    for spec_row in line_specs:
        rows = sorted(by_locus[spec_row["locus"]], key=lambda row: int(row["token_ordinal"]))
        check(len(rows) == int(spec_row["expected_token_count"]), f"token count changed: {spec_row['locus']}")
        check(" ".join(row["surface"] for row in rows) == spec_row["expected_written_line_eva"], f"written line changed: {spec_row['locus']}")
        check(all(row["unknown_v99r7"] == "0" for row in rows), f"new line incomplete: {spec_row['locus']}")

    cohort = read_tsv(artifacts / "EXPANDED_22_LINE_COHORT.tsv")
    old = read_tsv(OLD_COHORT)
    check(cohort[:131] == old, "the original GDT770 cohort changed")
    check(len(cohort) == 186, "expanded cohort is not 186 cells")
    check(len({row["cohort_id"] for row in cohort}) == 22, "expanded cohort is not 22 lines")
    check(len({row["page"] for row in cohort}) == 20, "expanded cohort is not 20 pages")
    targets = [row for row in cohort if row["is_target"] == "1"]
    check(Counter(row["surface"] for row in targets) == Counter({"ol": 15, "ckhy": 4, "ols": 3, "otar": 5}), "target inventory changed")
    new_targets = [row for row in targets if row["cohort_id"].startswith("G772-")]
    check(len(new_targets) == 10 and {row["surface"] for row in new_targets} == {"ol"}, "new target masks changed")
    check(all(row["structural_roles"] == "NONE" and row["frozen_non_target_default_de"] == "" for row in targets), "target role or default leaked")
    zero_fields = ("old_target_default_credit", "old_target_role_credit", "old_target_evidence_credit", "old_target_confidence_credit", "default_is_translation", "confirmed_lexeme", "confirmed_plaintext", "component_export_credit")
    check(all(row[field] == "0" for row in cohort for field in zero_fields), "cohort grants semantic credit")
    banned = re.compile(r"\b(?:Samen|Saatgut|Holz|Pulver|Wurzel|Drogen\w*)\b", re.IGNORECASE)
    check(not any(banned.search(row["frozen_non_target_default_de"]) for row in cohort[131:] if row["is_target"] == "0"), "retired literal remains in new reader")

    queried_map = {(row["locus"], row["token_ordinal"]): row for row in queried}
    edge_map = {(row["locus"], row["ordinal"]): row for row in edge_specs}
    override_map = {(row["locus"], row["ordinal"]): row for row in overrides}
    check(len(edge_map) == len(edge_specs) == 16, "edge specification count changed")
    check(len(override_map) == len(overrides) == 14, "override specification count changed")
    check(len(manual_readings) == 7, "manual recipe-reading count changed")
    expected_manual_slots = {
        (row["locus"], ordinal)
        for row in line_specs
        for ordinal in (() if row["full_branch_target_ordinals"] == "NONE" else tuple(int(value) for value in row["full_branch_target_ordinals"].split("|")))
    }
    check({(row["locus"], int(row["target_ordinal"])) for row in manual_readings} == expected_manual_slots, "manual recipe readings do not cover full branches")
    check(all(row[field] == "0" for row in manual_readings for field in ("score_credit", "default_is_translation", "confirmed_lexeme", "component_export_credit")), "manual reading grants score or semantic credit")
    check(read_tsv(artifacts / "OL_MANUAL_RECIPE_READING.tsv") == manual_readings, "manual reading artifact differs from fixed source")
    for row in cohort[131:]:
        key = (row["locus"], row["ordinal"])
        check(key in queried_map and queried_map[key]["surface"] == row["surface"], f"cohort cell not in guarded source: {key}")
        expected_roles = "NONE" if row["is_target"] == "1" or key not in edge_map else edge_map[key]["structural_roles"]
        check(row["structural_roles"] == expected_roles, f"role transfer mismatch: {key}")
        if row["is_target"] == "0":
            expected_default = override_map[key]["practical_default_de"] if key in override_map else queried_map[key]["v99r7_spoken_cell_de"]
            check(row["frozen_non_target_default_de"] == expected_default, f"display rerender mismatch: {key}")

    independent = import_independent_scorer()
    candidate_rows = read_tsv(CANDIDATES)
    weights = {row["penalty_id"]: int(row["weight"]) for row in read_tsv(PENALTIES)}
    slot_rows = read_tsv(OLD_SLOTS) + [{"cohort_id": row["cohort_id"], "ordinal": row["ordinal"], "target_mask_id": row["target_mask_id"], "predicate_only_close": "0", "provenance": "GDT771_NO_TARGET_INDEPENDENT_PREDICATE_ONLY_CLOSE_FOR_OL"} for row in cohort[131:] if row["is_target"] == "1"]
    core = independent.calculate_core(cohort, candidate_rows, weights, slot_rows)
    totals = score_totals(core)
    check({key: totals[key] for key in EXPECTED_OL} == EXPECTED_OL, "independent ol scores differ")
    check(len(core["contexts"]) == 27, "independent context count differs")
    check(all(row["selected_candidate_id"].endswith("_NULL") for row in core["target_decisions"].values()), "independent scorer selected a non-NULL policy")
    policy = {row["candidate_id"]: row for row in read_tsv(artifacts / "TARGET_POLICY_SCOREBOARD.tsv")}
    check(set(policy) == set(totals), "policy scoreboard candidate universe differs")
    for candidate_id, total in totals.items():
        check(int(policy[candidate_id]["total_penalty"]) == total, f"policy total differs: {candidate_id}")
        check(int(policy[candidate_id]["target_occurrence_count"]) == int(core["summaries"][candidate_id]["target_occurrence_count"]), f"occurrence count differs: {candidate_id}")

    decisions = {row["surface_provenance_only"]: row for row in read_tsv(artifacts / "TARGET_DECISIONS.tsv")}
    check(set(decisions) == set(TARGET_MASKS), "target decisions incomplete")
    check(decisions["ol"]["raw_minimum_candidates"] == "OL_NOMINAL_BASE|OL_POSITIONAL_RELATOR", "ol tie not exposed")
    check(all(row["formal_status"] == "OPAQUE_NULL" for row in decisions.values()), "formal decision changed")
    cases = read_tsv(artifacts / "OL_POSITIONAL_VS_NOMINAL_CASES.tsv")
    check(len(cases) == 15, "ol case atlas is not complete")
    full = [row for row in cases if row["full_branch_declared"] == "1"]
    collateral = [row for row in cases if row["case_class"] == "COLLATERAL_DIRECTIONAL_CONTROL"]
    old_cases = [row for row in cases if row["cohort_id"].startswith("G770-")]
    check(len(full) == 7 and len({row["page"] for row in full}) == 6, "full branch case/page count differs")
    check(len(collateral) == 3, "collateral control count differs")
    check(sum(int(row["positional_advantage_over_nominal"]) for row in full) == 28, "full-case advantage differs")
    check(sum(int(row["positional_advantage_over_nominal"]) for row in collateral) == -37, "collateral disadvantage differs")
    check(sum(int(row["positional_advantage_over_nominal"]) for row in old_cases) == 9, "old-case advantage differs")
    check(all(row["positional_requirements_hold"] == "1" and row["positional_penalty"] == "0" for row in full), "a declared full branch is not clean")

    display_mutation = copy.deepcopy(cohort)
    for row in display_mutation:
        if row["is_target"] == "0":
            row["frozen_non_target_default_de"] = "DISPLAY_MUTATION_WITH_ZERO_SCORE_CREDIT"
    mutation_core = independent.calculate_core(display_mutation, candidate_rows, weights, slot_rows)
    check(score_totals(mutation_core) == totals, "display prose changes the score")
    target_mutation = copy.deepcopy(cohort)
    for row in target_mutation:
        if row["is_target"] == "1":
            row["frozen_non_target_default_de"] = "FORBIDDEN_TARGET_HINT"
            row["structural_axes"] = "FORBIDDEN_AXIS_HINT"
    target_core = independent.calculate_core(target_mutation, candidate_rows, weights, slot_rows)
    check(score_totals(target_core) == totals, "target display or axes change the score")

    result = json.loads((artifacts / "RESULT.json").read_text(encoding="utf-8"))
    check(result["counts"]["score_node_count"] == 183, "result score-node count differs")
    check(result["ol_branch"] == {"all_old_case_positional_advantage_total": 9, "collateral_case_positional_advantage_total": -37, "full_case_positional_advantage_total": 28, "left_amount_or_value_qualified_occurrences": 7, "left_amount_or_value_qualified_pages": 6, "other_two_sided_qualified_occurrences": 4, "other_two_sided_qualified_pages": 4, "score_tie": True}, "result ol decomposition differs")
    check(all(value in (0, False, True, "page") or not isinstance(value, (int, bool)) for key, value in result["score_contract"].items() if key != "locked_source_hashes"), "unexpected score-contract scalar")
    local_root_marker = "/" + "home/"
    for path in [*(artifacts / name for name in outputs), EXP / "REPORT.md"]:
        text = path.read_text(encoding="utf-8", errors="replace")
        check(local_root_marker not in text and "PRIVATE KEY" not in text, f"private-machine or key text in {path.name}")

    replay_hashes: dict[str, str] = {}
    with tempfile.TemporaryDirectory(prefix="gdt772_validate_") as temporary:
        temp = Path(temporary)
        replay_artifacts, replay_report = temp / "artifacts", temp / "REPORT.md"
        completed = subprocess.run(["python3", str(RUN), "--output-dir", str(replay_artifacts), "--report-path", str(replay_report)], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        check(completed.returncode == 0, f"runner replay failed: {completed.stderr}")
        for name in outputs:
            check((replay_artifacts / name).read_bytes() == (artifacts / name).read_bytes(), f"byte replay differs: {name}")
            replay_hashes[name] = sha256(artifacts / name)
        check(replay_report.read_bytes() == (EXP / "REPORT.md").read_bytes(), "report byte replay differs")

    status = "PASS" if not failures else "FAIL"
    payload = {
        "experiment_id": "GDT772",
        "status": status,
        "checks": checks,
        "failures": failures,
        "independent_score_recalculation": True,
        "display_mutation_score_invariant": not failures or "display prose changes the score" not in failures,
        "target_hint_mutation_score_invariant": not failures or "target display or axes change the score" not in failures,
        "guard_stats": guard_stats,
        "byte_replay_outputs": len(replay_hashes),
        "artifact_sha256": replay_hashes,
        "f84_accessed": False,
        "f84r_accessed": False,
    }
    validation_path.parent.mkdir(parents=True, exist_ok=True)
    validation_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
