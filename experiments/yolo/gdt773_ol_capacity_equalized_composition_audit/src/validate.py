#!/usr/bin/env python3
"""Independent source, topology, renderer, safety, and replay checks for GDT773."""

from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import json
import re
import subprocess
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Callable, Iterable, Mapping, Sequence


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt773_ol_capacity_equalized_composition_audit"
SRC, ART = EXP / "src", EXP / "artifacts"
RUN, REPORT, VALIDATION = SRC / "run.py", EXP / "REPORT.md", ART / "VALIDATION.json"
G772 = ROOT / "experiments/yolo/gdt772_expanded_ol_branch_masked_rescore/artifacts"
G769 = ROOT / "experiments/yolo/gdt769_liquid_process_role_identity_dispatch"
G763 = ROOT / "experiments/yolo/gdt763_h1_content_vs_record_discriminator/artifacts"

PURE = (
    "OL_PARTITIVE_VON", "OL_DIRECTIONAL_AUS", "OL_QUANTIFIABLE_NOMINAL_HEAD",
    "OL_FIELD_SEQUENCE_MARKER", "OL_MEASURE_UNIT_COMPLEMENT",
)
COMPOSITE = "OL_RECORD_FIELD_OPERATOR"
A_ROLES = {"AMOUNT", "VALUE"}
C_ROLES = {"FIELD", "PATIENT", "SOURCE", "RESULT", "PROCESS", "ENDPOINT", "MATERIAL", "PREPARATION", "PRODUCT"}
SOURCE_ROLES = {"SOURCE", "MATERIAL"}
FIT = {
    "OL_PARTITIVE_VON": ("fit_von", "von_reading_de"),
    "OL_DIRECTIONAL_AUS": ("fit_aus", "aus_reading_de"),
    "OL_QUANTIFIABLE_NOMINAL_HEAD": ("fit_nominal", "nominal_reading_de"),
    "OL_FIELD_SEQUENCE_MARKER": ("fit_field_sequence", "field_sequence_reading_de"),
    "OL_MEASURE_UNIT_COMPLEMENT": ("fit_measure_unit", "measure_unit_reading_de"),
}
EXPECTED_TOPOLOGIES = {"AC": 7, "CA": 2, "CC": 2, "C0": 1, "A0": 1, "0A": 1, "AA": 1}
EXPECTED_FORMAL = {
    "OL_QUANTIFIABLE_NOMINAL_HEAD": 6, "OL_PARTITIVE_VON": 10,
    "OL_FIELD_SEQUENCE_MARKER": 13, "OL_MEASURE_UNIT_COMPLEMENT": 15,
    "OL_DIRECTIONAL_AUS": 24,
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def split_values(value: str) -> set[str]:
    return {item for item in value.split("|") if item and item != "NONE"}


def physical_folio(page: str) -> str:
    match = re.match(r"^(f\d+)", page)
    if match is None:
        raise AssertionError(f"cannot derive physical folio from {page}")
    return match.group(1)


def side_class(text: str) -> str:
    roles = split_values(text)
    if not roles:
        return "0"
    amount, content = bool(roles & A_ROLES), bool(roles & C_ROLES)
    if amount and content:
        return "MIXED"
    return "A" if amount else "C" if content else "OTHER"


def topology(left: str, right: str) -> str:
    table = {
        ("A", "C"): "AC", ("C", "A"): "CA", ("C", "C"): "CC", ("A", "A"): "AA",
        ("A", "0"): "A0", ("0", "A"): "0A", ("C", "0"): "C0", ("0", "C"): "0C",
    }
    return table.get((side_class(left), side_class(right)), "MIXED_OR_OTHER")


def literal_outputs() -> tuple[str, ...]:
    tree = ast.parse(RUN.read_text(encoding="utf-8"))
    nodes = [
        node for node in tree.body if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == "OUTPUT_NAMES" for target in node.targets)
    ]
    if len(nodes) != 1:
        raise AssertionError("runner must contain one literal OUTPUT_NAMES assignment")
    value = ast.literal_eval(nodes[0].value)
    if not isinstance(value, (list, tuple)) or not all(isinstance(item, str) for item in value):
        raise AssertionError("OUTPUT_NAMES is not a literal string sequence")
    return tuple(value)


def key(row: Mapping[str, object], fields: Sequence[str]) -> tuple[str, ...]:
    return tuple(str(row[field]) for field in fields)


def compare_rows(
    check: Callable[[bool, str], None], actual: Sequence[Mapping[str, object]],
    expected: Sequence[Mapping[str, object]], keys: Sequence[str], fields: Sequence[str], label: str,
) -> None:
    actual_map, expected_map = ({key(row, keys): row for row in rows} for rows in (actual, expected))
    check(len(actual_map) == len(actual), f"{label}: duplicate actual key")
    check(len(expected_map) == len(expected), f"{label}: duplicate expected key")
    check(set(actual_map) == set(expected_map), f"{label}: key universe differs")
    for row_id in sorted(set(actual_map) & set(expected_map)):
        for field in fields:
            check(str(actual_map[row_id].get(field, "")) == str(expected_map[row_id].get(field, "")), f"{label}: {row_id} field {field} differs")


def evidence_state(candidate: str, topo: str, right_roles: str, rule: Mapping[str, str]) -> tuple[str, str]:
    supports, contradictions = split_values(rule["support_topologies"]), split_values(rule["contradiction_topologies"])
    if candidate == "OL_DIRECTIONAL_AUS":
        if topo in supports and bool(split_values(right_roles) & SOURCE_ROLES):
            return "SUPPORT", "AC_WITH_RIGHT_SOURCE_OR_MATERIAL"
        if topo in contradictions:
            return "CONTRADICTION", "AC_OR_CA_WITHOUT_REQUIRED_DIRECTION"
        return "NEUTRAL", "NO_DIRECTIONAL_TEST"
    if topo in supports:
        return "SUPPORT", f"TOPOLOGY_{topo}"
    if topo in contradictions:
        return "CONTRADICTION", f"TOPOLOGY_{topo}"
    return "NEUTRAL", f"TOPOLOGY_{topo}"


def render_units(units: Iterable[str]) -> str:
    rendered = ""
    for unit in units:
        if unit in {":", ";"}:
            rendered = rendered.rstrip()
            if not rendered.endswith(unit):
                rendered += unit
        elif unit.startswith((":", ";")):
            punctuation, remainder = unit[0], unit[1:].lstrip()
            rendered = rendered.rstrip()
            if not rendered.endswith(punctuation):
                rendered += punctuation
            if remainder:
                rendered += " " + remainder
        elif unit.endswith(":"):
            if rendered:
                rendered = rendered.rstrip()
                if not rendered.endswith((":", ";")):
                    rendered += ";"
                rendered += " "
            rendered += unit
        else:
            rendered += (" " if rendered else "") + unit
    return rendered.strip()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifacts-dir", type=Path, default=ART)
    parser.add_argument("--validation-path", type=Path, default=VALIDATION)
    args = parser.parse_args()
    artifacts = args.artifacts_dir if args.artifacts_dir.is_absolute() else ROOT / args.artifacts_dir
    validation_path = args.validation_path if args.validation_path.is_absolute() else ROOT / args.validation_path
    checks, failures = 0, []

    def check(condition: bool, message: str) -> None:
        nonlocal checks
        checks += 1
        if not condition:
            failures.append(message)

    outputs = literal_outputs()
    check(len(outputs) == 20 and len(set(outputs)) == 20, "runner output contract changed")
    check(all((artifacts / name).is_file() for name in outputs), "a declared runner artifact is missing")

    locks = read_tsv(SRC / "SOURCE_LOCK.tsv")
    check(len(locks) == 8 and len({row["lock_id"] for row in locks}) == 8, "source-lock rows or ids changed")
    locked_hashes: dict[str, str] = {}
    for row in locks:
        path = Path(row["path"])
        check(not path.is_absolute() and ".." not in path.parts, f"unsafe locked path: {path}")
        full_path = ROOT / path
        check(full_path.is_file(), f"locked source missing: {path}")
        if full_path.is_file():
            locked_hashes[row["path"]] = sha256(full_path)
            check(locked_hashes[row["path"]] == row["expected_sha256"], f"locked hash differs: {path}")

    cases = read_tsv(G772 / "OL_POSITIONAL_VS_NOMINAL_CASES.tsv")
    cohort = read_tsv(G772 / "EXPANDED_22_LINE_COHORT.tsv")
    manual = read_tsv(G772 / "OL_MANUAL_RECIPE_READING.tsv")
    other_dictionary = read_tsv(G772 / "GDT772_4_WORKING_DICTIONARY.tsv")
    case_specs = read_tsv(SRC / "OL_15_CASE_READING_SPECS.tsv")
    model_specs = read_tsv(SRC / "FIVE_READING_MODEL_SPECS.tsv")
    topo_rules = read_tsv(SRC / "TOPOLOGY_EVIDENCE_RULE_SPECS.tsv")
    winner_gates = read_tsv(SRC / "WINNER_GATE_SPECS.tsv")
    dispatch_rules = sorted(read_tsv(SRC / "DISPATCH_RULE_SPECS.tsv"), key=lambda row: int(row["priority"]))
    judgments = read_tsv(SRC / "INDEPENDENT_READER_JUDGMENT_SPECS.tsv")
    polish_specs = read_tsv(SRC / "MANUAL_LINE_POLISH_SPECS.tsv")
    historical = read_tsv(G769 / "src/HISTORICAL_RELATOR_ANALOGUES.tsv")
    amount_atlas = read_tsv(G763 / "OL_16_SLOT_FUNCTION_ATLAS.tsv")
    census = read_tsv(G769 / "artifacts/TARGET_5_CENSUS.tsv")

    check(len(cases) == len(case_specs) == 15, "fifteen-case count changed")
    check([row["case_id"] for row in cases] == [row["case_id"] for row in case_specs], "case order differs")
    check(len({row["case_id"] for row in cases}) == 15, "case ids are not unique")
    check({row["candidate_id"] for row in topo_rules} == set(PURE), "topology candidate universe differs")
    check({row["candidate_id"] for row in model_specs} == set(PURE) | {COMPOSITE}, "model universe differs")
    check({row["gate_id"] for row in winner_gates} == {f"G{i:02d}" for i in range(8)}, "winner-gate universe differs")
    check([int(row["priority"]) for row in dispatch_rules] == list(range(1, 6)), "dispatch priorities differ")
    check(all(row["confirmed_lexeme"] == "0" and row["component_export_credit"] == "0" for row in case_specs + model_specs + dispatch_rules), "an authored spec grants semantic credit")
    check(len(manual) == 7 and all(row["score_credit"] == "0" for row in manual), "manual audit count or score credit differs")
    check(not any("SOURCE" in row["manual_preference"] for row in manual), "manual audit introduces a source reading")

    line_rows: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
    for row in cohort:
        line_rows[row["cohort_id"]].append(row)
    for rows in line_rows.values():
        rows.sort(key=lambda row: int(row["ordinal"]))
    target_by_key = {
        (row["locus"], row["ordinal"]): row for row in cohort
        if row["is_target"] == "1" and row["surface"] == "ol"
    }
    spec_by_case = {row["case_id"]: row for row in case_specs}
    observable_expected: list[dict[str, object]] = []
    for case, spec in zip(cases, case_specs):
        check((case["locus"], case["ordinal"]) == (spec["locus"], spec["ordinal"]), f"case locus differs: {case['case_id']}")
        target = target_by_key.get((case["locus"], case["ordinal"]))
        check(target is not None, f"locked cohort lacks ol target: {case['case_id']}")
        left_slot, right_slot = int(bool(split_values(case["left_roles"]))), int(bool(split_values(case["right_roles"])))
        observable_expected.append({
            "case_id": case["case_id"], "occurrence_id": case["occurrence_id"], "cohort_id": case["cohort_id"],
            "locus": case["locus"], "page": case["page"], "physical_folio": physical_folio(case["page"]),
            "ordinal": case["ordinal"], "left_roles": case["left_roles"], "right_roles": case["right_roles"],
            "left_slot": left_slot, "right_slot": right_slot, "bridge_slot": int(bool(left_slot and right_slot)),
            "topology": topology(case["left_roles"], case["right_roles"]),
            "right_source_or_material": int(bool(split_values(case["right_roles"]) & SOURCE_ROLES)),
            "discovery_focal": case["full_branch_declared"], "context_class": spec["context_class"],
            "context_eva": spec["context_eva"], "written_line_eva": " ".join(row["surface"] for row in line_rows[case["cohort_id"]]),
            "target_surface_provenance_only": target["surface"] if target else "",
            "target_identity_credit": 0, "confirmed_lexeme": 0, "component_export_credit": 0,
        })
    topo_counts = Counter(str(row["topology"]) for row in observable_expected)
    check(dict(topo_counts) == EXPECTED_TOPOLOGIES, "independent topology census differs")
    check(sum(int(row["right_source_or_material"]) for row in observable_expected if row["topology"] == "AC") == 0, "AC case unexpectedly supplies source direction")
    compare_rows(check, read_tsv(artifacts / "OL_15_OBSERVABLE_CASES.tsv"), observable_expected,
                 ("case_id",), tuple(observable_expected[0]), "observable atlas")

    folios = sorted({str(row["physical_folio"]) for row in observable_expected}, key=lambda value: int(value[1:]))
    check(len(folios) == 10, "physical-folio count differs")
    capacity_expected: list[dict[str, object]] = []
    for row in observable_expected:
        mask = f"L{row['left_slot']}R{row['right_slot']}B{row['bridge_slot']}"
        penalty = 2 - int(row["left_slot"]) - int(row["right_slot"])
        for candidate in PURE:
            capacity_expected.append({
                "candidate_id": candidate, "case_id": row["case_id"], "locus": row["locus"],
                "physical_folio": row["physical_folio"], "left_slot": row["left_slot"], "right_slot": row["right_slot"],
                "bridge_slot": row["bridge_slot"], "capacity_mask": mask, "base_penalty": penalty,
                "candidate_specific_capacity_credit": 0, "equality_pass": 1,
            })
    compare_rows(check, read_tsv(artifacts / "BASE_CAPACITY_AUDIT.tsv"), capacity_expected,
                 ("candidate_id", "case_id"), tuple(capacity_expected[0]), "base capacity")
    check(len(capacity_expected) == 75, "capacity row count differs")
    for case_id in {str(row["case_id"]) for row in capacity_expected}:
        check(len({(row["capacity_mask"], row["base_penalty"]) for row in capacity_expected if row["case_id"] == case_id}) == 1, f"casewise capacity differs: {case_id}")

    capacity_loo_expected: list[dict[str, object]] = []
    for held in folios:
        totals = {candidate: sum(int(row["base_penalty"]) for row in capacity_expected if row["candidate_id"] == candidate and row["physical_folio"] != held) for candidate in PURE}
        check(len(set(totals.values())) == 1, f"holdout capacity differs: {held}")
        remaining = sum(row["physical_folio"] != held for row in observable_expected)
        for candidate in PURE:
            capacity_loo_expected.append({"held_physical_folio": held, "candidate_id": candidate, "remaining_case_count": remaining, "aggregate_base_penalty": totals[candidate], "all_candidates_equal": 1})
    compare_rows(check, read_tsv(artifacts / "CAPACITY_LEAVE_ONE_FOLIO_OUT.tsv"), capacity_loo_expected,
                 ("held_physical_folio", "candidate_id"), tuple(capacity_loo_expected[0]), "capacity holdout")

    rule_by_candidate = {row["candidate_id"]: row for row in topo_rules}
    score_expected: list[dict[str, object]] = []
    for row in observable_expected:
        for candidate in PURE:
            rule = rule_by_candidate[candidate]
            state, trigger = evidence_state(candidate, str(row["topology"]), str(row["right_roles"]), rule)
            cost_field = {"SUPPORT": "support_cost", "NEUTRAL": "neutral_cost", "CONTRADICTION": "contradiction_cost"}[state]
            score_expected.append({
                "candidate_id": candidate, "case_id": row["case_id"], "locus": row["locus"],
                "physical_folio": row["physical_folio"], "topology": row["topology"], "discovery_focal": row["discovery_focal"],
                "evidence_state": state, "trigger_code": trigger, "evidence_penalty": int(rule[cost_field]),
                "common_capacity_mask": f"L{row['left_slot']}R{row['right_slot']}B{row['bridge_slot']}",
                "common_capacity_credit": 0, "semantic_role_credit": 0, "confirmed_lexeme": 0, "component_export_credit": 0,
            })
    compare_rows(check, read_tsv(artifacts / "CANDIDATE_CASE_SCORE.tsv"), score_expected,
                 ("candidate_id", "case_id"), tuple(score_expected[0]), "formal case score")
    formal_totals = {candidate: sum(int(row["evidence_penalty"]) for row in score_expected if row["candidate_id"] == candidate) for candidate in PURE}
    check(formal_totals == EXPECTED_FORMAL, "independent formal totals differ")
    full_min = min(formal_totals.values())
    full_minima = sorted(candidate for candidate, score in formal_totals.items() if score == full_min)
    check(full_minima == ["OL_QUANTIFIABLE_NOMINAL_HEAD"], "formal winner is not unique nominal head")

    loo_expected: list[dict[str, object]] = []
    all_fold_wins = {candidate: True for candidate in PURE}
    for held in folios:
        fold = {
            candidate: sum(int(row["evidence_penalty"]) for row in score_expected if row["candidate_id"] == candidate and row["physical_folio"] != held)
            for candidate in PURE
        }
        fold_min = min(fold.values())
        fold_minima = sorted(candidate for candidate, score in fold.items() if score == fold_min)
        remaining = sum(row["physical_folio"] != held for row in observable_expected)
        for candidate in PURE:
            rival = min(score for other, score in fold.items() if other != candidate)
            unique = fold_minima == [candidate]
            all_fold_wins[candidate] &= unique
            loo_expected.append({
                "held_physical_folio": held, "candidate_id": candidate, "remaining_case_count": remaining,
                "fold_score": fold[candidate], "best_rival_score": rival,
                "margin_over_best_rival": rival - fold[candidate], "fold_minimum_candidates": "|".join(fold_minima),
                "candidate_unique_fold_winner": int(unique),
            })
    compare_rows(check, read_tsv(artifacts / "LEAVE_ONE_FOLIO_OUT.tsv"), loo_expected,
                 ("held_physical_folio", "candidate_id"), tuple(loo_expected[0]), "formal holdout")
    nominal_holdouts = [row for row in loo_expected if row["candidate_id"] == "OL_QUANTIFIABLE_NOMINAL_HEAD"]
    check(all(int(row["candidate_unique_fold_winner"]) == 1 for row in nominal_holdouts), "nominal head loses a folio holdout")
    check(min(int(row["margin_over_best_rival"]) for row in nominal_holdouts) == 2, "minimum nominal holdout margin differs")

    capacity_equal = all(row["equality_pass"] == 1 for row in capacity_expected) and all(row["all_candidates_equal"] == 1 for row in capacity_loo_expected)
    scoreboard_expected: list[dict[str, object]] = []
    gates_expected: list[dict[str, object]] = []
    for candidate in PURE:
        rows = [row for row in score_expected if row["candidate_id"] == candidate]
        support = [row for row in rows if row["evidence_state"] == "SUPPORT"]
        nondiscovery = [row for row in support if row["discovery_focal"] == "0"]
        contradictions = [row for row in rows if row["evidence_state"] == "CONTRADICTION"]
        support_pages = len({row["physical_folio"] for row in support})
        nondiscovery_pages = len({row["physical_folio"] for row in nondiscovery})
        best_rival = min(score for other, score in formal_totals.items() if other != candidate)
        board = {
            "candidate_id": candidate, "support_occurrences": len(support), "support_pages": support_pages,
            "nondiscovery_support_occurrences": len(nondiscovery), "nondiscovery_support_pages": nondiscovery_pages,
            "neutral_occurrences": sum(row["evidence_state"] == "NEUTRAL" for row in rows),
            "contradiction_occurrences": len(contradictions), "contradiction_pages": len({row["physical_folio"] for row in contradictions}),
            "total_score": formal_totals[candidate], "best_rival_score": best_rival,
            "margin_over_best_rival": best_rival - formal_totals[candidate],
            "full_minimum": int(candidate in full_minima), "all_leave_one_folio_out_unique_wins": int(all_fold_wins[candidate]),
        }
        ac_pages = len({row["physical_folio"] for row in support if row["topology"] == "AC"})
        ca_pages = len({row["physical_folio"] for row in support if row["topology"] == "CA"})
        gate_checks = (
            ("G00", capacity_equal, "casewise_and_leave_folio_capacity_equal"),
            ("G01", len(support) >= 4 and support_pages >= 4, f"{len(support)}_occurrences__{support_pages}_pages"),
            ("G02", len(nondiscovery) >= 2 and nondiscovery_pages >= 2, f"{len(nondiscovery)}_occurrences__{nondiscovery_pages}_pages"),
            ("G03", int(board["margin_over_best_rival"]) >= 4, f"margin_{board['margin_over_best_rival']}"),
            ("G04", len(contradictions) == 0, f"{len(contradictions)}_contradictions"),
            ("G05", all_fold_wins[candidate], "all_folds_unique" if all_fold_wins[candidate] else "not_all_folds_unique"),
            ("G06", candidate != "OL_QUANTIFIABLE_NOMINAL_HEAD" or (ac_pages >= 2 and ca_pages >= 2), "not_applicable" if candidate != "OL_QUANTIFIABLE_NOMINAL_HEAD" else f"AC_{ac_pages}_pages__CA_{ca_pages}_pages"),
            ("G07", full_minima == [candidate], "|".join(full_minima)),
        )
        board["all_winner_gates_pass"] = int(all(passed for _, passed, _ in gate_checks))
        scoreboard_expected.append(board)
        for gate_id, passed, observed in gate_checks:
            gates_expected.append({"candidate_id": candidate, "gate_id": gate_id, "passed": int(passed), "observed": observed})
    compare_rows(check, read_tsv(artifacts / "CANDIDATE_SCOREBOARD.tsv"), scoreboard_expected,
                 ("candidate_id",), tuple(scoreboard_expected[0]), "formal scoreboard")
    compare_rows(check, read_tsv(artifacts / "GATE_AUDIT.tsv"), gates_expected,
                 ("candidate_id", "gate_id"), ("candidate_id", "gate_id", "passed", "observed"), "winner gates")
    check([row["candidate_id"] for row in scoreboard_expected if row["all_winner_gates_pass"] == 1] == ["OL_QUANTIFIABLE_NOMINAL_HEAD"], "winner gates select a different candidate")

    score_map = {(str(row["candidate_id"]), str(row["case_id"])): row for row in score_expected}
    focal_expected: list[dict[str, object]] = []
    for row in observable_expected:
        if row["discovery_focal"] != "1":
            continue
        nominal = score_map[("OL_QUANTIFIABLE_NOMINAL_HEAD", str(row["case_id"]))]
        von = score_map[("OL_PARTITIVE_VON", str(row["case_id"]))]
        delta = int(nominal["evidence_penalty"]) - int(von["evidence_penalty"])
        focal_expected.append({
            "case_id": row["case_id"], "locus": row["locus"], "physical_folio": row["physical_folio"],
            "topology": row["topology"], "nominal_penalty": nominal["evidence_penalty"], "von_penalty": von["evidence_penalty"],
            "nominal_minus_von": delta, "focal_selection_neutral": int(delta == 0),
        })
    compare_rows(check, read_tsv(artifacts / "FOCAL_SELECTION_DELTA_AUDIT.tsv"), focal_expected,
                 ("case_id",), tuple(focal_expected[0]), "focal delta")
    check(len(focal_expected) == 7 and all(row["topology"] == "AC" and row["nominal_minus_von"] == 0 for row in focal_expected), "focal seven are not neutral AC cases")

    practical_expected: list[dict[str, object]] = []
    for spec in case_specs:
        for candidate in PURE:
            fit_column, reading_column = FIT[candidate]
            cost = spec[fit_column]
            practical_expected.append({
                "case_id": spec["case_id"], "locus": spec["locus"], "ordinal": spec["ordinal"], "candidate_id": candidate,
                "fit_cost": cost, "fit_grade": {"0": "NATURAL", "1": "USABLE", "2": "STRAINED", "3": "CONTRADICTORY"}[cost],
                "candidate_reading_de": spec[reading_column], "reason_de": spec["reason_de"],
                "evidence_refs": spec["evidence_refs"], "score_is_plaintext_credit": 0,
            })
    compare_rows(check, read_tsv(artifacts / "OL_FIVE_WAY_PRACTICAL_FIT.tsv"), practical_expected,
                 ("candidate_id", "case_id"), tuple(practical_expected[0]), "practical fit")

    rule_matches: dict[str, dict[str, str]] = {}
    for spec in case_specs:
        matches = [rule for rule in dispatch_rules if spec["context_class"] in split_values(rule["context_classes"])]
        check(len(matches) == 1, f"dispatch coverage is not exactly one: {spec['case_id']}")
        if len(matches) == 1:
            rule_matches[spec["case_id"]] = matches[0]
    contextual_expected: list[dict[str, object]] = []
    for spec in case_specs:
        rule = rule_matches[spec["case_id"]]
        fit_column = FIT[rule["fit_source_candidate"]][0]
        contextual_expected.append({
            "case_id": spec["case_id"], "locus": spec["locus"], "ordinal": spec["ordinal"], "context_eva": spec["context_eva"],
            "context_class": spec["context_class"], "dispatch_rule_id": rule["rule_id"], "complexity_branch": rule["complexity_branch"],
            "selected_function": rule["selected_function"], "selected_default_de": spec["default_surface_de"],
            "rule_default_de": rule["default_surface_de"], "strongest_rival_de": spec["alternative_de"],
            "selected_local_fit_cost": spec[fit_column], "portable_rule_de": rule["portable_rule_de"],
            "default_is_translation": 0, "confirmed_lexeme": 0, "component_export_credit": 0,
        })
    compare_rows(check, read_tsv(artifacts / "OL_CONTEXTUAL_DEFAULTS.tsv"), contextual_expected,
                 ("case_id",), tuple(contextual_expected[0]), "contextual defaults")
    branch_counts = Counter(str(row["complexity_branch"]) for row in contextual_expected)
    check(branch_counts == Counter({"ASSOCIATE_QUANTITY_CONTENT": 7, "ADVANCE_OR_CLOSE_FIELD": 8}), "contextual branch split differs")
    check(all(int(row["selected_local_fit_cost"]) == 0 for row in contextual_expected), "contextual dispatch selects a non-natural fit")
    check(Counter(str(row["dispatch_rule_id"]) for row in contextual_expected) == Counter({"G773-D01": 5, "G773-D02": 2, "G773-D03": 2, "G773-D04": 1, "G773-D05": 5}), "dispatch rule usage differs")

    model_by_id = {row["candidate_id"]: row for row in model_specs}
    practical_board_expected: list[dict[str, object]] = []
    for candidate in PURE:
        rows = [row for row in practical_expected if row["candidate_id"] == candidate]
        raw = sum(int(row["fit_cost"]) for row in rows)
        complexity = int(model_by_id[candidate]["model_complexity_cost"])
        practical_board_expected.append({
            "candidate_id": candidate, "natural_cases": sum(row["fit_grade"] == "NATURAL" for row in rows),
            "usable_or_better_cases": sum(row["fit_grade"] in {"NATURAL", "USABLE"} for row in rows),
            "contradictory_cases": sum(row["fit_grade"] == "CONTRADICTORY" for row in rows),
            "raw_practical_fit_cost": raw, "model_complexity_cost": complexity,
            "adjusted_practical_cost": raw + complexity, "case_coverage": 15,
        })
    composite_cost = int(model_by_id[COMPOSITE]["model_complexity_cost"])
    practical_board_expected.append({
        "candidate_id": COMPOSITE, "natural_cases": 15, "usable_or_better_cases": 15, "contradictory_cases": 0,
        "raw_practical_fit_cost": 0, "model_complexity_cost": composite_cost,
        "adjusted_practical_cost": composite_cost, "case_coverage": 15,
    })
    practical_board_expected.sort(key=lambda row: (int(row["adjusted_practical_cost"]), str(row["candidate_id"])))
    for rank, row in enumerate(practical_board_expected, start=1):
        row["rank"] = rank
        row["selected_working_renderer"] = int(rank == 1 and row["candidate_id"] == COMPOSITE)
    compare_rows(check, read_tsv(artifacts / "PRACTICAL_MODEL_SCOREBOARD.tsv"), practical_board_expected,
                 ("candidate_id",), tuple(practical_board_expected[0]), "practical scoreboard")
    pure_costs = {str(row["candidate_id"]): int(row["raw_practical_fit_cost"]) for row in practical_board_expected if row["candidate_id"] != COMPOSITE}
    check(pure_costs == {
        "OL_FIELD_SEQUENCE_MARKER": 6, "OL_QUANTIFIABLE_NOMINAL_HEAD": 9,
        "OL_MEASURE_UNIT_COMPLEMENT": 29, "OL_PARTITIVE_VON": 31, "OL_DIRECTIONAL_AUS": 44,
    }, "pure practical totals differ")
    check(practical_board_expected[0]["candidate_id"] == COMPOSITE and practical_board_expected[0]["adjusted_practical_cost"] == 2 and practical_board_expected[1]["adjusted_practical_cost"] == 6, "contextual practical winner or margin differs")

    judgments_by_case: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
    for row in judgments:
        judgments_by_case[row["case_id"]].append(row)
    check(len(judgments) == 30 and set(judgments_by_case) == set(spec_by_case), "reader judgment coverage differs")
    check(all(len(rows) == 2 and {row["reader_id"] for row in rows} == {"R_APOTHECARY", "R_SCRIBE"} for rows in judgments_by_case.values()), "reader pairing differs")
    check(all(row["primary_candidate"] in PURE and row["second_candidate"] in PURE and row["primary_candidate"] != row["second_candidate"] for row in judgments), "reader judgment candidate is malformed")
    check(all(row["changed_files"] == "0" for row in judgments), "an independent reader changed files")
    contextual_by_case = {str(row["case_id"]): row for row in contextual_expected}
    disagreement_expected: list[dict[str, object]] = []
    agreement_cases: list[str] = []
    for case_id in [row["case_id"] for row in case_specs]:
        apothecary = next(row for row in judgments_by_case[case_id] if row["reader_id"] == "R_APOTHECARY")
        scribe = next(row for row in judgments_by_case[case_id] if row["reader_id"] == "R_SCRIBE")
        agreed = apothecary["primary_candidate"] == scribe["primary_candidate"]
        if agreed:
            agreement_cases.append(case_id)
        selected = contextual_by_case[case_id]
        disagreement_expected.append({
            "case_id": case_id, "locus": spec_by_case[case_id]["locus"],
            "apothecary_primary": apothecary["primary_candidate"], "scribe_primary": scribe["primary_candidate"],
            "exact_primary_agreement": int(agreed), "contextual_selected_function": selected["selected_function"],
            "contextual_default_de": selected["selected_default_de"], "disagreement_preserved": int(not agreed),
        })
    compare_rows(check, read_tsv(artifacts / "INDEPENDENT_READER_DISAGREEMENT.tsv"), disagreement_expected,
                 ("case_id",), tuple(disagreement_expected[0]), "reader disagreement")
    check(len(agreement_cases) == 6, "exact reader agreement count differs")
    check(all(next(row for row in judgments_by_case[case_id] if row["reader_id"] == "R_APOTHECARY")["primary_candidate"] == "OL_FIELD_SEQUENCE_MARKER" for case_id in agreement_cases), "reader agreement outside field/sequence cases")

    reader_count_expected: list[dict[str, object]] = []
    for reader_id in ("R_APOTHECARY", "R_SCRIBE"):
        rows = [row for row in judgments if row["reader_id"] == reader_id]
        counts = Counter(row["primary_candidate"] for row in rows)
        for candidate in PURE:
            reader_count_expected.append({
                "reader_id": reader_id, "reader_background": rows[0]["reader_background"],
                "candidate_id": candidate, "primary_count": counts[candidate], "case_count": 15, "changed_files": 0,
            })
    compare_rows(check, read_tsv(artifacts / "READER_PRIMARY_COUNTS.tsv"), reader_count_expected,
                 ("reader_id", "candidate_id"), tuple(reader_count_expected[0]), "reader counts")
    reader_count_map = {(str(row["reader_id"]), str(row["candidate_id"])): int(row["primary_count"]) for row in reader_count_expected}
    check(reader_count_map == {
        ("R_APOTHECARY", "OL_PARTITIVE_VON"): 0, ("R_APOTHECARY", "OL_DIRECTIONAL_AUS"): 0,
        ("R_APOTHECARY", "OL_QUANTIFIABLE_NOMINAL_HEAD"): 7, ("R_APOTHECARY", "OL_FIELD_SEQUENCE_MARKER"): 8,
        ("R_APOTHECARY", "OL_MEASURE_UNIT_COMPLEMENT"): 0, ("R_SCRIBE", "OL_PARTITIVE_VON"): 5,
        ("R_SCRIBE", "OL_DIRECTIONAL_AUS"): 0, ("R_SCRIBE", "OL_QUANTIFIABLE_NOMINAL_HEAD"): 1,
        ("R_SCRIBE", "OL_FIELD_SEQUENCE_MARKER"): 7, ("R_SCRIBE", "OL_MEASURE_UNIT_COMPLEMENT"): 2,
    }, "reader primary distribution differs")

    historical_by_id = {row["analogue_id"]: row for row in historical}
    historical_expected: list[dict[str, object]] = []
    for model in model_specs:
        for analogue_id in model["historical_analogue_ids"].split("|"):
            analogue = historical_by_id[analogue_id]
            historical_expected.append({
                "candidate_id": model["candidate_id"], "short_label_de": model["short_label_de"],
                "analogue_id": analogue_id, "date_or_witness": analogue["date_or_witness"], "source": analogue["source"],
                "class": analogue["class"], "historical_architecture_de": analogue["historical_architecture_de"],
                "discriminates_de": analogue["discriminates_de"], "caveat_de": analogue["caveat_de"],
                "url": analogue["url"], "voynich_identity_credit": 0,
            })
    compare_rows(check, read_tsv(artifacts / "HISTORICAL_COMPOSITION_BRIDGE.tsv"), historical_expected,
                 ("candidate_id", "analogue_id"), tuple(historical_expected[0]), "historical bridge")
    check(len(historical_expected) == 14 and all(row["voynich_identity_credit"] == 0 for row in historical_expected), "historical bridge count or credit differs")

    ol_rows = [row for row in census if row["surface"] == "ol"]
    check(len(ol_rows) == 1, "global census lacks unique ol row")
    exact_ol, amount_contacts = int(ol_rows[0]["reader_exact_occurrences"]), len(amount_atlas)
    amount_deck = sum(row["topology"] in {"AC", "CA", "AA", "A0", "0A"} for row in observable_expected)
    global_expected = {
        "surface": "ol", "reader_exact_ol": exact_ol, "known_amount_contacts": amount_contacts,
        "known_amount_contact_rate": f"{amount_contacts / exact_ol:.6f}", "deck_cases_with_any_A_side": amount_deck,
        "deck_case_count": 15, "deck_is_amount_enriched": 1, "fixed_global_unit_selected": 0, "specific_substance_selected": 0,
    }
    compare_rows(check, read_tsv(artifacts / "GLOBAL_AMOUNT_CONTACT_CHECK.tsv"), [global_expected],
                 ("surface",), tuple(global_expected), "global amount check")
    check((amount_contacts, exact_ol, amount_deck) == (16, 376, 12), "global or deck amount count differs")
    check(amount_deck / 15 > amount_contacts / exact_ol, "fifteen-case deck is not amount enriched")

    contextual_by_key = {(str(row["locus"]), str(row["ordinal"])): row for row in contextual_expected}
    other_defaults = {row["whole_form"]: row["concrete_replaceable_default_de"] for row in other_dictionary}
    selected_ids = {case["cohort_id"] for case in cases}
    selected_cohort = [row for row in cohort if row["cohort_id"] in selected_ids]
    token_expected: list[dict[str, object]] = []
    for row in selected_cohort:
        target_key = (row["locus"], row["ordinal"])
        if target_key in contextual_by_key:
            default = contextual_by_key[target_key]["selected_default_de"]
            source, render_once = contextual_by_key[target_key]["dispatch_rule_id"], 1
        elif row["is_target"] == "1":
            check(row["surface"] in other_defaults, f"missing inherited target default: {row['surface']}")
            default, source, render_once = other_defaults[row["surface"]], "GDT772_OTHER_TARGET_WORKING_DICTIONARY", 1
        elif row["frozen_non_target_default_de"] == "NONE":
            check(row["span_member_role"] == "CONSUMED", f"NONE default is not consumed: {row['locus']}@{row['ordinal']}")
            default, source, render_once = "in der vorigen Mehrtoken-Mengenform enthalten", "INHERITED_CONSUMED_SPAN_MEMBER", 0
        else:
            default, source = row["frozen_non_target_default_de"], "GDT772_INHERITED_NON_OL_DEFAULT"
            render_once = int(row["span_member_role"] != "CONSUMED")
        token_expected.append({
            "cohort_id": row["cohort_id"], "locus": row["locus"], "physical_folio": physical_folio(row["page"]),
            "ordinal": row["ordinal"], "surface": row["surface"], "is_ol_target": int(target_key in contextual_by_key),
            "working_default_de": default, "default_source": source, "render_once": render_once,
            "span_id": row["span_id"], "span_member_role": row["span_member_role"],
            "default_is_translation": 0, "confirmed_lexeme": 0, "component_export_credit": 0,
        })
    compare_rows(check, read_tsv(artifacts / "GDT773_11_LINE_TOKEN_DEFAULTS.tsv"), token_expected,
                 ("cohort_id", "ordinal"), tuple(token_expected[0]), "token defaults")
    check(len(token_expected) == 93 and sum(int(row["render_once"]) for row in token_expected) == 91, "token or practical-unit count differs")
    check(sum(int(row["is_ol_target"]) for row in token_expected) == 15, "token-ledger ol count differs")
    check(all(str(row["working_default_de"]).strip() for row in token_expected), "token ledger contains an empty default")
    consumed = [row for row in token_expected if row["span_member_role"] == "CONSUMED"]
    check(len(consumed) == 2 and all(row["render_once"] == 0 for row in consumed), "consumed span membership differs")
    for row in consumed:
        owners = [candidate for candidate in token_expected if candidate["span_id"] == row["span_id"] and candidate["span_member_role"] == "OWNER"]
        check(len(owners) == 1 and owners[0]["render_once"] == 1, f"consumed span lacks one owner: {row['span_id']}")

    reader_expected: list[dict[str, object]] = []
    for cohort_id in sorted(selected_ids, key=lambda value: int(value.split("-L")[-1])):
        rows = sorted([row for row in token_expected if row["cohort_id"] == cohort_id], key=lambda row: int(row["ordinal"]))
        units = [str(row["working_default_de"]) for row in rows if int(row["render_once"])]
        defaults = [str(row["working_default_de"]) for row in rows if int(row["is_ol_target"])]
        reader_expected.append({
            "cohort_id": cohort_id, "locus": rows[0]["locus"], "physical_folio": rows[0]["physical_folio"],
            "source_token_count": len(rows), "practical_unit_count": len(units),
            "ol_target_count": sum(int(row["is_ol_target"]) for row in rows),
            "written_line_eva": " ".join(f"[{row['surface']}]" if int(row["is_ol_target"]) else str(row["surface"]) for row in rows),
            "ol_contextual_defaults_de": " | ".join(defaults), "working_reading_de": render_units(units),
            "all_source_tokens_accounted": 1, "inherited_non_ol_defaults_revalidated": 0,
            "default_is_translation": 0, "confirmed_plaintext": 0,
        })
    compare_rows(check, read_tsv(artifacts / "GDT773_11_LINE_READER.tsv"), reader_expected,
                 ("cohort_id",), tuple(reader_expected[0]), "line reader")
    check(len(reader_expected) == 11 and sum(int(row["ol_target_count"]) for row in reader_expected) == 15, "line reader coverage differs")
    check(sum(int(row["practical_unit_count"]) for row in reader_expected) == 91, "line reader unit count differs")

    polish_by_id = {row["cohort_id"]: row for row in polish_specs}
    check(len(polish_specs) == len(polish_by_id) == 11 and set(polish_by_id) == selected_ids, "manual polish coverage differs")
    check(all(row["ol_direction_valid"] == "1" and row["polished_is_translation"] == "0" and row["confirmed_lexeme"] == "0" for row in polish_specs), "manual polish direction or claim ceiling differs")
    source_by_id: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
    for row in selected_cohort:
        source_by_id[row["cohort_id"]].append(row)
    polished_expected: list[dict[str, object]] = []
    for reader in reader_expected:
        cohort_id = str(reader["cohort_id"])
        spec, source_rows = polish_by_id[cohort_id], source_by_id[cohort_id]
        check(spec["locus"] == reader["locus"], f"polish locus differs: {cohort_id}")
        non_ol = [row for row in source_rows if not (row["is_target"] == "1" and row["surface"] == "ol")]
        polished_expected.append({
            "cohort_id": cohort_id, "locus": reader["locus"], "risk_level": spec["risk_level"], "ol_direction_valid": 1,
            "source_token_count": len(source_rows), "ol_target_count": reader["ol_target_count"], "non_ol_token_count": len(non_ol),
            "non_ol_untyped_count": sum(row["structural_roles"] == "NONE" for row in non_ol),
            "non_ol_display_only_count": sum(row["current_provenance"] == "GDT734_COMPLETE_CELL__DISPLAY_ONLY_UNTYPED" for row in non_ol),
            "non_ol_nonexact_count": sum(row["reader_exact"] == "0" for row in non_ol),
            "written_line_eva": reader["written_line_eva"], "mechanical_working_reading_de": reader["working_reading_de"],
            "polished_record_reading_de": spec["polished_record_reading_de"], "manual_note_de": spec["manual_note_de"],
            "editorial_condensation": 1, "all_ol_targets_preserved": 1, "polished_is_translation": spec["polished_is_translation"],
            "confirmed_lexeme": spec["confirmed_lexeme"], "confirmed_plaintext": 0,
        })
    compare_rows(check, read_tsv(artifacts / "GDT773_11_LINE_POLISHED_RECORD_READER.tsv"), polished_expected,
                 ("cohort_id",), tuple(polished_expected[0]), "polished reader")
    check(sum(int(row["non_ol_token_count"]) for row in polished_expected) == 78, "polished reader non-ol count differs")
    check(sum(int(row["non_ol_untyped_count"]) for row in polished_expected) == 33, "polished reader untyped count differs")
    check(sum(int(row["non_ol_display_only_count"]) for row in polished_expected) == 29, "polished reader display-only count differs")
    check(sum(int(row["non_ol_nonexact_count"]) for row in polished_expected) == 3, "polished reader nonexact count differs")
    check(all(int(row["ol_direction_valid"]) == 1 and int(row["all_ol_targets_preserved"]) == 1 for row in polished_expected), "polished reader loses an ol direction")

    dictionary = read_tsv(artifacts / "GDT773_OL_WORKING_DICTIONARY.tsv")
    check(len(dictionary) == 1 and dictionary[0]["whole_form"] == "ol", "working dictionary row differs")
    if dictionary:
        check(dictionary[0]["formal_invariant_working_default"] == "Ansatz-/Zubereitungsposten", "formal fallback differs")
        check(dictionary[0]["selected_contextual_model"] == COMPOSITE, "dictionary contextual model differs")
        check(dictionary[0]["confidence_level"] == "C1_STRUCTURAL_COMPOSITION__C0_LEXEME", "dictionary confidence differs")
        check(dictionary[0]["aus_status"].startswith("kein Primärfall"), "dictionary aus status differs")
        check(all(dictionary[0][field] == "0" for field in ("default_is_translation", "confirmed_lexeme", "confirmed_plaintext", "component_export_credit")), "dictionary grants semantic credit")

    result = json.loads((artifacts / "RESULT.json").read_text(encoding="utf-8"))
    expected_counts = {
        "ol_case_count": 15, "line_count": 11, "physical_folio_count": 10, "capacity_row_count": 75,
        "formal_case_score_count": 75, "practical_fit_row_count": 75, "contextual_default_count": 15,
        "reader_judgment_count": 30, "reader_source_token_count": 93, "reader_practical_unit_count": 91,
        "reader_non_ol_token_count": 78, "reader_non_ol_untyped_count": 33,
        "reader_non_ol_display_only_count": 29, "reader_non_ol_nonexact_count": 3,
        "historical_bridge_row_count": 14, "topology_counts": dict(sorted(EXPECTED_TOPOLOGIES.items())),
    }
    check(result["experiment_id"] == "GDT773" and result["outputs"] == list(outputs), "result id or output contract differs")
    check(result["source_hashes"] == locked_hashes, "result source hash map differs")
    check(result["counts"] == expected_counts, "result count block differs")
    check(result["formal_topology_result"]["winner"] == "OL_QUANTIFIABLE_NOMINAL_HEAD" and result["formal_topology_result"]["all_scores"] == formal_totals, "result formal winner or totals differ")
    check(result["formal_topology_result"]["winner_full_margin"] == 4 and result["formal_topology_result"]["focal_ac_nominal_von_delta"] == 0, "result formal margin or focal delta differs")
    check(result["formal_topology_result"]["capacity_equalized"] is True and result["formal_topology_result"]["all_leave_one_folio_out_unique_wins"] is True, "result capacity or holdout flag differs")
    check(result["practical_result"] == {
        "winner": COMPOSITE, "winner_adjusted_cost": 2, "best_pure": "OL_FIELD_SEQUENCE_MARKER",
        "best_pure_adjusted_cost": 6, "association_default_count": 7, "field_default_count": 8,
    }, "result practical block differs")
    check(result["independent_readers"] == {
        "exact_primary_agreements": 6, "apothecary_nominal": 7, "apothecary_field": 8,
        "scribe_von": 5, "scribe_field": 7, "scribe_unit": 2, "scribe_nominal": 1, "aus_primary_count": 0,
    }, "result reader block differs")
    check(result["global_check"]["reader_exact_ol"] == 376 and result["global_check"]["amount_contacts"] == 16 and result["global_check"]["deck_is_amount_enriched"] is True, "result global block differs")
    check(abs(float(result["global_check"]["amount_contact_rate"]) - 16 / 376) < 1e-15, "result global rate differs")
    check(all(value is False for value in result["scope"].values()), "result scope claims new or sealed access")
    check(result["claim_ceiling"] == {
        "confirmed_lexemes": 0, "confirmed_translations": 0, "confirmed_plaintext_clauses": 0,
        "component_export_credit": 0, "eva_latin_credit": 0, "defaults_are_replaceable": True,
    }, "result claim ceiling differs")
    check("CONTEXTUAL_ASSOCIATION7_FIELD8" in result["status"], "result status omits association/field split")

    local_root_marker = "/" + "home/"
    private_key_marker = "PRIVATE" + " KEY"
    access_key_marker = "AK" + "IA"
    scan_paths = [*(artifacts / name for name in outputs), REPORT, *sorted(SRC.glob("*.tsv")), RUN, Path(__file__).resolve()]
    for path in scan_paths:
        content = path.read_text(encoding="utf-8", errors="replace")
        check(local_root_marker not in content, f"absolute local home path leaked: {path.name}")
        check(private_key_marker not in content and access_key_marker not in content, f"credential-like text leaked: {path.name}")

    replay_hashes: dict[str, str] = {}
    report_hash = ""
    with tempfile.TemporaryDirectory(prefix="gdt773_validate_") as temporary:
        temp = Path(temporary)
        replay_artifacts, replay_report = temp / "artifacts", temp / "REPORT.md"
        completed = subprocess.run(
            ["python3", str(RUN), "--output-dir", str(replay_artifacts), "--report-path", str(replay_report)],
            cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        check(completed.returncode == 0, f"runner replay failed: {completed.stderr}")
        if completed.returncode == 0:
            for name in outputs:
                check((replay_artifacts / name).read_bytes() == (artifacts / name).read_bytes(), f"byte replay differs: {name}")
                replay_hashes[name] = sha256(artifacts / name)
            check(replay_report.read_bytes() == REPORT.read_bytes(), "report byte replay differs")
            report_hash = sha256(REPORT)

    status = "PASS" if not failures else "FAIL"
    payload = {
        "experiment_id": "GDT773", "status": status, "checks": checks, "failures": failures,
        "source_hash_locks_verified": len(locked_hashes), "independent_topology_recalculation": True,
        "independent_capacity_recalculation": True, "independent_formal_score_recalculation": True,
        "independent_dispatch_and_reader_reconstruction": True,
        "topology_counts": dict(sorted(topo_counts.items())), "formal_scores": formal_totals,
        "minimum_nominal_holdout_margin": min(int(row["margin_over_best_rival"]) for row in nominal_holdouts),
        "association_default_count": branch_counts["ASSOCIATE_QUANTITY_CONTENT"],
        "field_default_count": branch_counts["ADVANCE_OR_CLOSE_FIELD"],
        "reader_exact_primary_agreements": len(agreement_cases), "reader_source_tokens": len(token_expected),
        "reader_practical_units": sum(int(row["render_once"]) for row in token_expected),
        "polished_reader_rows": len(polished_expected), "polished_reader_all_ol_directions_valid": all(int(row["ol_direction_valid"]) == 1 for row in polished_expected),
        "byte_replay_outputs": len(replay_hashes), "artifact_sha256": replay_hashes,
        "report_sha256": report_hash, "f84_accessed": False, "f84r_accessed": False,
    }
    validation_path.parent.mkdir(parents=True, exist_ok=True)
    validation_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
