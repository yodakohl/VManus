#!/usr/bin/env python3
"""Independent, target-blind audit of the repaired F76S001 prescore gate.

This script never imports the production runner, never opens TARGET_RESULT.json,
and never parses the manuscript interlinear or crosswalk.  Those two large inputs
are read only as opaque bytes for SHA-256 verification.  All numerical checks use
independently written scalar code and synthetic panels.
"""

from __future__ import annotations

import ast
import csv
import hashlib
import io
import json
import math
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RUNNER = HERE / "run_f76s001.py"
VALIDATOR = HERE / "validate_f76s001.py"
CONTROL_RESULT = HERE / "CONTROL_RESULT.json"
TARGET_RESULT = HERE / "TARGET_RESULT.json"
PREREG = ROOT / "experiments/semantic_assumptions/hypotheses/F76S001_LINE_ENTRY_SELECTOR_PREREGISTRATION.md"
AMENDMENT = ROOT / "experiments/semantic_assumptions/hypotheses/F76S001_PRESCORE_EXECUTION_AMENDMENT.md"
SOURCE_ALIGNMENT_AUDIT = ROOT / "experiments/semantic_assumptions/results/f76r_keylike_sequence_source_audit.md"
SOURCE_CROSSWALK = ROOT / "experiments/semantic_assumptions/results/existing_human_current_locus_crosswalk.tsv"
INPUT = ROOT / "experiments/semantic_assumptions/results/pre_grounding_interlinear.tsv"
CONTROL_REPORT = ROOT / "experiments/semantic_assumptions/results/f76s001_line_entry_selector_control_report.md"

READINGS = ("ZL3b", "IT2a", "RF1b")
CHANNELS = ("carrier", "q_state", "role_path")
PAIRING = (
    (1, "f76r.4", "f76r.5", "s"),
    (2, "f76r.7", "f76r.8", "d"),
    (3, "f76r.10", "f76r.11", "q"),
    (4, "f76r.14", "f76r.15", "s"),
    (5, "f76r.18", "f76r.19", "o"),
    (6, "f76r.22", "f76r.23", "l"),
    (7, "f76r.27", "f76r.28", "k"),
    (8, "f76r.31", "f76r.32", "r"),
    (9, "f76r.37", "f76r.38", "s"),
)
LOCI = tuple(row[2] for row in PAIRING)
TARGET = (0, 3, 8)
EPS = 1e-12

EXPECTED_CONTROL_ASSERTIONS = {
    "combo_count_84",
    "planted_passes",
    "planted_unique_tail",
    "negative_fails",
    "channel_only_fails_deletion",
    "pair_leverage_fails_pair_gate",
    "reading_disagreement_fails",
    "conservative_four_way_top_tie",
    "degenerate_rejected",
    "deterministic_repeat",
    "row_contract_accepts_exact_27",
    "row_contract_rejects_duplicate",
    "row_contract_rejects_missing",
    "row_contract_rejects_scope_drift",
    "row_contract_rejects_page_drift",
}

FROZEN_HASHES = {
    "input_sha256": "8052a51fa37ad467e754be39648336ec4014442dab5e223daab2e77efaba4a43",
    "source_alignment_audit_sha256": "27593399b74b00e72cbd939519d324d5ace1c4846b457435263b92a3c3104744",
    "source_crosswalk_sha256": "4a128ed3d4b87a9d804a336a6c22ced65839fa39c83f3ecf45092bbc64f2eabc",
}


class IndependentDegenerateOrbit(RuntimeError):
    pass


class FakeInput:
    """In-memory stand-in used to exercise the validator's actual load()."""

    def __init__(self, text: str):
        self.text = text

    def open(self, *args: Any, **kwargs: Any) -> io.StringIO:
        return io.StringIO(self.text)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def triples() -> list[tuple[int, int, int]]:
    # Deliberately avoid itertools.combinations, which production uses.
    return [(a, b, c) for a in range(9) for b in range(a + 1, 9) for c in range(b + 1, 9)]


COMBOS = triples()


def independent_edit_distance(left: tuple[str, ...], right: tuple[str, ...]) -> int:
    grid = [[0] * (len(right) + 1) for _ in range(len(left) + 1)]
    for i in range(len(left) + 1):
        grid[i][0] = i
    for j in range(len(right) + 1):
        grid[0][j] = j
    for i in range(1, len(left) + 1):
        for j in range(1, len(right) + 1):
            substitution = grid[i - 1][j - 1] + (left[i - 1] != right[j - 1])
            grid[i][j] = min(grid[i - 1][j] + 1, grid[i][j - 1] + 1, substitution)
    return grid[-1][-1]


def mean(values: list[float]) -> float:
    return sum(values) / len(values)


def median(values: list[float]) -> float:
    ordered = sorted(values)
    midpoint = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[midpoint]
    return (ordered[midpoint - 1] + ordered[midpoint]) / 2


def population_sd(values: list[float]) -> float:
    center = mean(values)
    return math.sqrt(sum((value - center) ** 2 for value in values) / len(values))


def feature(carrier: str, q_state: bool, role_path: tuple[str, ...], surface: str) -> dict[str, Any]:
    return {"carrier": carrier, "q_state": q_state, "role_path": role_path, "surface": surface}


def channel_values(left: dict[str, Any], right: dict[str, Any]) -> dict[str, float]:
    denominator = max(len(left["role_path"]), len(right["role_path"]))
    if denominator == 0:
        raise ValueError("empty role path")
    return {
        "carrier": float(left["carrier"] == right["carrier"]),
        "q_state": float(left["q_state"] == right["q_state"]),
        "role_path": 1.0 - independent_edit_distance(left["role_path"], right["role_path"]) / denominator,
    }


def independent_pair_score(left: dict[str, Any], right: dict[str, Any], channels: tuple[str, ...]) -> float:
    values = channel_values(left, right)
    return mean([values[channel] for channel in channels])


def independent_triplet_score(
    panel: list[dict[str, Any]], combo: tuple[int, int, int], channels: tuple[str, ...]
) -> float:
    a, b, c = combo
    return mean([
        independent_pair_score(panel[a], panel[b], channels),
        independent_pair_score(panel[a], panel[c], channels),
        independent_pair_score(panel[b], panel[c], channels),
    ])


def independent_score_panel(
    panel: dict[str, list[dict[str, Any]]], channels: tuple[str, ...] = CHANNELS
) -> dict[str, Any]:
    if tuple(panel) != READINGS:
        raise ValueError("reading order drift")
    scores: dict[str, list[float]] = {}
    zscores: dict[str, list[float]] = {}
    for reading in READINGS:
        if len(panel[reading]) != 9:
            raise ValueError("expected nine features")
        values = [independent_triplet_score(panel[reading], combo, channels) for combo in COMBOS]
        deviation = population_sd(values)
        if deviation <= EPS:
            raise IndependentDegenerateOrbit(reading)
        center = mean(values)
        scores[reading] = values
        zscores[reading] = [(value - center) / deviation for value in values]

    offset = COMBOS.index(TARGET)
    synchronous = [min(zscores[reading][index] for reading in READINGS) for index in range(84)]
    observed_sync = synchronous[offset]
    exact_tail = sum(value >= observed_sync - EPS for value in synchronous)
    strictly_greater = sum(value > observed_sync + EPS for value in synchronous)
    tied = sum(abs(value - observed_sync) <= EPS for value in synchronous)

    ranks: dict[str, int] = {}
    effects: dict[str, float] = {}
    pair_gate: dict[str, bool] = {}
    pair_details: dict[str, Any] = {}
    for reading in READINGS:
        observed = scores[reading][offset]
        ranks[reading] = 1 + sum(value > observed + EPS for value in scores[reading])
        effects[reading] = observed - median(scores[reading])
        all_pairs = [
            independent_pair_score(panel[reading][a], panel[reading][b], channels)
            for a in range(9)
            for b in range(a + 1, 9)
        ]
        target_pairs = [
            independent_pair_score(panel[reading][TARGET[0]], panel[reading][TARGET[1]], channels),
            independent_pair_score(panel[reading][TARGET[0]], panel[reading][TARGET[2]], channels),
            independent_pair_score(panel[reading][TARGET[1]], panel[reading][TARGET[2]], channels),
        ]
        pair_median = median(all_pairs)
        pair_gate[reading] = all(value > pair_median + EPS for value in target_pairs)
        pair_details[reading] = {"all_pair_median": pair_median, "target_pair_scores": target_pairs}

    orbit_digest = hashlib.sha256(json.dumps(
        {reading: [format(value, ".17g") for value in scores[reading]] for reading in READINGS},
        sort_keys=True,
    ).encode()).hexdigest()
    return {
        "channels": list(channels),
        "combo_count": len(COMBOS),
        "target_positions_one_based": [1, 4, 9],
        "target_synchronous_z": observed_sync,
        "exact_tail_count": exact_tail,
        "strictly_greater_count": strictly_greater,
        "tied_at_target_count": tied,
        "exact_p": exact_tail / 84,
        "reading_ranks": ranks,
        "reading_effects": effects,
        "minimum_effect": min(effects.values()),
        "pair_gate": pair_gate,
        "pair_details": pair_details,
        "surface_duplicate_veto": {
            reading: len({panel[reading][index]["surface"] for index in TARGET}) == 3
            for reading in READINGS
        },
        "orbit_digest": orbit_digest,
    }


def independent_evaluate(panel: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    primary = independent_score_panel(panel)
    leave_one_out: dict[str, Any] = {}
    for omitted in CHANNELS:
        retained = tuple(channel for channel in CHANNELS if channel != omitted)
        result = independent_score_panel(panel, retained)
        leave_one_out[omitted] = {
            "retained_channels": list(retained),
            "exact_tail_count": result["exact_tail_count"],
            "exact_p": result["exact_p"],
            "target_synchronous_z": result["target_synchronous_z"],
        }
    gates = {
        "complete_support": all(len(panel[reading]) == 9 for reading in READINGS),
        "surface_duplicate_veto": all(primary["surface_duplicate_veto"].values()),
        "primary_exact_p": primary["exact_p"] <= 4 / 84 + EPS,
        "all_reading_rank": all(rank <= 3 for rank in primary["reading_ranks"].values()),
        "minimum_effect": primary["minimum_effect"] >= 0.10 - EPS,
        "all_target_pairs_above_median": all(primary["pair_gate"].values()),
        "all_channel_deletions": all(item["exact_p"] <= 4 / 84 + EPS for item in leave_one_out.values()),
    }
    return {"primary": primary, "leave_one_channel_out": leave_one_out, "gates": gates, "pass": all(gates.values())}


def synthetic_panel(kind: str) -> dict[str, list[dict[str, Any]]]:
    planted = [
        feature("A", False, ("BARE",), f"surface-{i}")
        if i in TARGET
        else feature(chr(66 + i), bool(i % 2), (f"ROLE_{i}",), f"surface-{i}")
        for i in range(9)
    ]
    negative = [
        feature("A", False, ("R0",), "n0"),
        feature("Z", True, ("SAME",), "n1"),
        feature("Z", True, ("SAME",), "n2"),
        feature("B", True, ("R3", "X"), "n3"),
        feature("Z", True, ("SAME",), "n4"),
        feature("C", False, ("R5",), "n5"),
        feature("D", True, ("R6",), "n6"),
        feature("E", False, ("R7",), "n7"),
        feature("F", True, ("R8", "Y"), "n8"),
    ]
    channel_only = [
        feature("A" if i in TARGET else chr(66 + i), bool(i % 2), (f"ROLE_{i}",), f"c-{i}")
        for i in range(9)
    ]
    pair_leverage = [
        feature("A", False, ("SAME",), "p0"),
        feature("B", True, ("R1",), "p1"),
        feature("C", False, ("R2",), "p2"),
        feature("A", False, ("SAME",), "p3"),
        feature("D", True, ("R4",), "p4"),
        feature("E", False, ("R5",), "p5"),
        feature("F", True, ("R6",), "p6"),
        feature("G", False, ("R7",), "p7"),
        feature("H", True, ("DIFFERENT", "LONG"), "p8"),
    ]
    tied_positions = {0, 1, 3, 8}
    tie_top = [
        feature("T", False, ("TIE",), f"tie-{i}")
        if i in tied_positions
        else feature(f"U{i}", bool(i % 2), (f"UNIQUE_{i}",), f"tie-{i}")
        for i in range(9)
    ]
    if kind == "reading_disagreement":
        return {
            "ZL3b": [dict(item) for item in planted],
            "IT2a": [dict(item) for item in planted],
            "RF1b": [dict(item) for item in negative],
        }
    source = {
        "planted": planted,
        "negative": negative,
        "channel_only": channel_only,
        "pair_leverage": pair_leverage,
        "tie_top": tie_top,
    }[kind]
    return {reading: [dict(item) for item in source] for reading in READINGS}


def equivalent(left: Any, right: Any) -> bool:
    if isinstance(left, bool) or isinstance(right, bool):
        return type(left) is type(right) and left == right
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        return math.isclose(float(left), float(right), rel_tol=0.0, abs_tol=EPS)
    if isinstance(left, dict) and isinstance(right, dict):
        return left.keys() == right.keys() and all(equivalent(left[key], right[key]) for key in left)
    if isinstance(left, (list, tuple)) and isinstance(right, (list, tuple)):
        return len(left) == len(right) and all(equivalent(a, b) for a, b in zip(left, right))
    return left == right


def synthetic_rows() -> list[dict[str, str]]:
    return [
        {
            "edition": reading,
            "locus": locus,
            "page": "f76r",
            "grammar_scope": "CONFIRMED_PROSE",
            "surface": f"synthetic_{reading}_{locus}",
            "role_sequence": "Q_BOUND_E",
            "line_carrier": "",
        }
        for reading in READINGS
        for locus in LOCI
    ]


def rows_as_tsv(rows: list[dict[str, str]]) -> str:
    fields = ("edition", "locus", "page", "grammar_scope", "surface", "role_sequence", "line_carrier")
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fields, delimiter="\t", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()


def extract_functions(source: str, names: set[str]) -> Any:
    tree = ast.parse(source)
    selected = [node for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in names]
    if {node.name for node in selected} != names:
        raise AssertionError(f"missing extracted functions: {names - {node.name for node in selected}}")
    module = ast.Module(body=selected, type_ignores=[])
    ast.fix_missing_locations(module)
    return compile(module, "<isolated-audit>", "exec")


def actual_runner_row_contract(runner_source: str) -> dict[str, bool]:
    namespace: dict[str, Any] = {"READINGS": READINGS, "PAIRING": PAIRING, "Any": Any}
    exec(extract_functions(runner_source, {"validate_target_rows", "row_contract_rejects"}), namespace)
    validate = namespace["validate_target_rows"]
    valid = synthetic_rows()
    duplicate = valid + [dict(valid[0])]
    missing = valid[1:]
    scope = [dict(row) for row in valid]
    scope[0]["grammar_scope"] = "EXCLUDED"
    page = [dict(row) for row in valid]
    page[0]["page"] = "f76v"
    return {
        "accepts_exact_27": len(validate(valid)) == 27,
        "rejects_duplicate": namespace["row_contract_rejects"](duplicate),
        "rejects_missing": namespace["row_contract_rejects"](missing),
        "rejects_scope": namespace["row_contract_rejects"](scope),
        "rejects_page": namespace["row_contract_rejects"](page),
    }


def actual_validator_row_contract(validator_source: str) -> dict[str, bool]:
    namespace: dict[str, Any] = {"READINGS": READINGS, "LOCI": LOCI, "csv": csv, "Any": Any}
    exec(extract_functions(validator_source, {"load"}), namespace)

    def outcome(rows: list[dict[str, str]]) -> bool:
        namespace["INPUT"] = FakeInput(rows_as_tsv(rows))
        try:
            panel = namespace["load"]()
        except RuntimeError:
            return False
        return tuple(panel) == READINGS and all(len(panel[reading]) == 9 for reading in READINGS)

    valid = synthetic_rows()
    duplicate = valid + [dict(valid[0])]
    missing = valid[1:]
    scope = [dict(row) for row in valid]
    scope[0]["grammar_scope"] = "EXCLUDED"
    page = [dict(row) for row in valid]
    page[0]["page"] = "f76v"
    return {
        "accepts_exact_27": outcome(valid),
        "rejects_duplicate": not outcome(duplicate),
        "rejects_missing": not outcome(missing),
        "rejects_scope": not outcome(scope),
        "rejects_page": not outcome(page),
    }


def literal_assignment(source: str, name: str) -> Any:
    tree = ast.parse(source)
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == name for target in node.targets):
            return ast.literal_eval(node.value)
    raise AssertionError(f"literal assignment not found: {name}")


def main() -> None:
    target_absent_before = not TARGET_RESULT.exists()
    if not target_absent_before:
        raise RuntimeError("TARGET_RESULT.json exists; target-blind audit refused")

    runner_source = RUNNER.read_text(encoding="utf-8")
    validator_source = VALIDATOR.read_text(encoding="utf-8")
    prereg_text = PREREG.read_text(encoding="utf-8")
    amendment_text = AMENDMENT.read_text(encoding="utf-8")
    source_audit_text = SOURCE_ALIGNMENT_AUDIT.read_text(encoding="utf-8")
    control_report_text = CONTROL_REPORT.read_text(encoding="utf-8")
    controls = json.loads(CONTROL_RESULT.read_text(encoding="utf-8"))

    current_bindings = {
        "input_sha256": sha256(INPUT),  # opaque-byte hash only
        "source_alignment_audit_sha256": sha256(SOURCE_ALIGNMENT_AUDIT),
        "source_crosswalk_sha256": sha256(SOURCE_CROSSWALK),  # opaque-byte hash only
        "preregistration_sha256": sha256(PREREG),
        "prescore_amendment_sha256": sha256(AMENDMENT),
        "runner_sha256": sha256(RUNNER),
        "validator_sha256": sha256(VALIDATOR),
    }

    reconstructed: dict[str, Any] = {}
    for kind in ("planted", "negative", "channel_only", "pair_leverage", "reading_disagreement"):
        reconstructed[kind] = independent_evaluate(synthetic_panel(kind))
    reconstructed["tie_top"] = independent_score_panel(synthetic_panel("tie_top"))

    degenerate_rejected = False
    degenerate_row = [feature("A", False, ("SAME",), f"d-{i}") for i in range(9)]
    try:
        independent_evaluate({reading: [dict(item) for item in degenerate_row] for reading in READINGS})
    except IndependentDegenerateOrbit:
        degenerate_rejected = True

    runner_rows = actual_runner_row_contract(runner_source)
    validator_rows = actual_validator_row_contract(validator_source)
    tie = reconstructed["tie_top"]
    strict_tail_mutation_would_fail = (
        tie["exact_tail_count"] == 4
        and tie["strictly_greater_count"] == 0
        and tie["tied_at_target_count"] == 4
        and tie["strictly_greater_count"] != 4
    )
    independent_assertions = {
        "combo_count_84": len(COMBOS) == 84 and len(set(COMBOS)) == 84,
        "planted_passes": reconstructed["planted"]["pass"],
        "planted_unique_tail": reconstructed["planted"]["primary"]["exact_tail_count"] == 1,
        "negative_fails": not reconstructed["negative"]["pass"],
        "channel_only_fails_deletion": not reconstructed["channel_only"]["gates"]["all_channel_deletions"],
        "pair_leverage_fails_pair_gate": not reconstructed["pair_leverage"]["gates"]["all_target_pairs_above_median"],
        "reading_disagreement_fails": not reconstructed["reading_disagreement"]["pass"],
        "conservative_four_way_top_tie": strict_tail_mutation_would_fail,
        "degenerate_rejected": degenerate_rejected,
        "deterministic_repeat": independent_evaluate(synthetic_panel("planted")) == reconstructed["planted"],
        "row_contract_accepts_exact_27": runner_rows["accepts_exact_27"] and validator_rows["accepts_exact_27"],
        "row_contract_rejects_duplicate": runner_rows["rejects_duplicate"] and validator_rows["rejects_duplicate"],
        "row_contract_rejects_missing": runner_rows["rejects_missing"] and validator_rows["rejects_missing"],
        "row_contract_rejects_scope_drift": runner_rows["rejects_scope"] and validator_rows["rejects_scope"],
        "row_contract_rejects_page_drift": runner_rows["rejects_page"] and validator_rows["rejects_page"],
    }

    expected_validator_contract_tokens = {
        '"control_identity"',
        '"control_status"',
        '"control_assertions"',
        '"control_bindings"',
        '"target_identity"',
        '"target_bindings"',
        '"target_pairing"',
        '"target_claim_ceiling"',
        '"row_cardinality_and_scope"',
        '"primary_complete"',
        '"gates"',
        '"decision"',
        '"target_status"',
        '"control_result_sha256"',
    }
    validator_contract_complete = all(token in validator_source for token in expected_validator_contract_tokens)
    validator_contract_complete = validator_contract_complete and all(
        f'checks[f"loo_{{omitted}}"]' in validator_source for _unused in [0]
    )

    checks = {
        "target_absent_before": target_absent_before,
        "combination_space_exact": COMBOS == sorted(COMBOS) and len(COMBOS) == 84 and len(set(COMBOS)) == 84,
        "all_six_control_results_reconstructed": equivalent(reconstructed, controls.get("results")),
        "all_15_assertions_reconstructed": (
            set(independent_assertions) == EXPECTED_CONTROL_ASSERTIONS
            and all(independent_assertions.values())
            and independent_assertions == controls.get("assertions")
        ),
        "artifact_assertion_membership_exact": set(controls.get("assertions", {})) == EXPECTED_CONTROL_ASSERTIONS,
        "runner_assertion_membership_exact": set(literal_assignment(runner_source, "EXPECTED_CONTROL_ASSERTIONS")) == EXPECTED_CONTROL_ASSERTIONS,
        "validator_assertion_membership_exact": set(literal_assignment(validator_source, "EXPECTED_CONTROL_ASSERTIONS")) == EXPECTED_CONTROL_ASSERTIONS,
        "control_identity_status_gate": (
            controls.get("experiment") == "F76S001"
            and controls.get("mode") == "CONTROLS"
            and controls.get("status") == "PASS_CONTROLS_TARGET_STILL_FORBIDDEN"
            and controls.get("all_controls_pass") is True
        ),
        "separate_alignment_crosswalk_bindings": (
            current_bindings["source_alignment_audit_sha256"] != current_bindings["source_crosswalk_sha256"]
            and current_bindings["source_alignment_audit_sha256"] == FROZEN_HASHES["source_alignment_audit_sha256"]
            and current_bindings["source_crosswalk_sha256"] == FROZEN_HASHES["source_crosswalk_sha256"]
            and "SOURCE_ALIGNMENT_AUDIT" in runner_source
            and "SOURCE_CROSSWALK" in runner_source
            and "SOURCE_ALIGNMENT_AUDIT" in validator_source
            and "SOURCE_CROSSWALK" in validator_source
        ),
        "all_current_bindings_match_control": controls.get("bindings") == current_bindings,
        "input_hash_matches_without_parse": current_bindings["input_sha256"] == FROZEN_HASHES["input_sha256"],
        "tie_fixture_exact_and_mutation_sensitive": strict_tail_mutation_would_fail,
        "runner_row_contract_all_five_cases": all(runner_rows.values()),
        "validator_row_contract_all_five_cases": all(validator_rows.values()),
        "future_validator_contract_complete": validator_contract_complete,
        "preregistration_and_amendment_scope_intact": (
            "`C(9,3)=84`" in prereg_text
            and "exactly the four three-member subsets" in amendment_text
            and "each of the 27 frozen" in amendment_text
            and "Complete future validation contract" in amendment_text
        ),
        "source_claim_ceiling_preserved": (
            "approximate alignment" in source_audit_text
            and "no authorial ownership" in runner_source
            and "no authorial ownership" in validator_source
        ),
        "control_report_matches_final_artifact": (
            "All 15 frozen assertions pass: `True`" in control_report_text
            and "conservative tail 4, strictly-greater count 0, and tied count 4" in control_report_text
        ),
    }

    target_absent_after = not TARGET_RESULT.exists()
    checks["target_absent_after"] = target_absent_after
    payload = {
        "audit": "F76S001_REPAIRED_PRESCORE",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "check_count": len(checks),
        "all_checks_pass": all(checks.values()),
        "independent_control_assertions": independent_assertions,
        "runner_row_contract": runner_rows,
        "validator_row_contract": validator_rows,
        "tie_fixture": {
            "inclusive_tail": tie["exact_tail_count"],
            "strictly_greater": tie["strictly_greater_count"],
            "tied_at_target": tie["tied_at_target_count"],
            "strict_tail_mutation_would_fail": strict_tail_mutation_would_fail,
        },
        "reconstructed_primary_orbit_count": 6 * 3 * 84,
        "reconstructed_leave_one_out_orbit_count": 5 * 3 * 3 * 84,
        "bindings": current_bindings,
        "target_result_absent_before": target_absent_before,
        "target_result_absent_after": target_absent_after,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    if not payload["all_checks_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
