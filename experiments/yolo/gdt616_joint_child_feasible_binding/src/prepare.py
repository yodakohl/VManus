#!/usr/bin/env python3
"""Build the deterministic prospective GDT616 search registration only."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
EXP = ROOT / "experiments/yolo/gdt616_joint_child_feasible_binding"
OUT = EXP / "artifacts/REGISTERED_SEARCH.json"

INPUTS = {
    "experiments/yolo/gdt608_compositional_stem_orientation/artifacts/merge_tree.tsv":
        "2098c71be9da13b483cf2561e06412276d8c60aa32e72520e8877f8f5d53090a",
    "experiments/yolo/gdt614_core_run_macro_recovery/artifacts/REGISTERED_MODEL.json":
        "ed841dc254a961650a8bda8bdc6024b67655f6bdc96e5dab2aec02f1686ecc42",
    "experiments/yolo/gdt614_core_run_macro_recovery/artifacts/REGISTERED_TRANSITIONS.tsv":
        "bf26bfeaa258a65e3c22a8e035cf6ddec30557307ebc9c7619c662b12324271e",
    "experiments/yolo/gdt615_joint_output_permutation_recovery/artifacts/REGISTERED_SEARCH.json":
        "138cb3860a9927e8095534b293836271797a654e5e2797e12b0fadb0689e2089",
    "experiments/yolo/gdt615_joint_output_permutation_recovery/artifacts/REGISTERED_TRAIN_SUBSTRINGS.txt":
        "5b6859d8656f63cf8e8cf89221ae8ff1dea345e135a6cd012248b9b4c4ff14a9",
    "experiments/yolo/gdt615_joint_output_permutation_recovery/artifacts/stage1/STAGE1_RESULT.json":
        "f9f1e0ee8096d191ab454971c1e6218fed29586881d6cafbc9b790bff4332f3e",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def load_json(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def build() -> dict:
    source_rows = []
    for relative, expected in INPUTS.items():
        path = ROOT / relative
        actual = sha256(path)
        if actual != expected:
            raise SystemExit(f"input hash drift: {relative}: {actual} != {expected}")
        source_rows.append({"bytes": path.stat().st_size, "path": relative, "sha256": actual})

    merge_path = ROOT / next(path for path in INPUTS if path.endswith("merge_tree.tsv"))
    with merge_path.open(encoding="utf-8", newline="") as handle:
        merges = list(csv.DictReader(handle, delimiter="\t"))
    if len(merges) != 64 or [int(row["rank"]) for row in merges] != list(range(1, 65)):
        raise SystemExit("registered merge rank drift")

    model = load_json(
        "experiments/yolo/gdt614_core_run_macro_recovery/artifacts/REGISTERED_MODEL.json"
    )
    prior = load_json(
        "experiments/yolo/gdt615_joint_output_permutation_recovery/artifacts/REGISTERED_SEARCH.json"
    )
    terminal = load_json(
        "experiments/yolo/gdt615_joint_output_permutation_recovery/artifacts/stage1/STAGE1_RESULT.json"
    )
    substring_path = ROOT / prior["registered_train_substrings"]["path"]
    substring_count = sum(1 for _ in substring_path.open(encoding="ascii"))
    if substring_count != 28101:
        raise SystemExit(f"TRAIN substring count drift: {substring_count}")
    if terminal["status"] != "MAPPING_BOUND_PASS__FULL_WORLD_INFEASIBLE":
        raise SystemExit("GDT615 terminal prior drift")

    transitive = []
    for row in prior["registered_inputs"]:
        name = Path(row["path"]).name
        if name in {"units.tsv", "synthetic_train.txt", "synthetic_held.txt", "lm_fit.txt", "lm_confirm.txt"}:
            access = {
                "units.tsv": "PRECOMMIT_TRAIN_ALLOWED",
                "synthetic_train.txt": "PRECOMMIT_TRAIN_ALLOWED",
                "lm_fit.txt": "PRECOMMIT_TRAIN_ALLOWED",
                "synthetic_held.txt": "AFTER_THREE_WORLD_COMMIT_ONLY",
                "lm_confirm.txt": "AFTER_THREE_WORLD_COMMIT_AND_HELD_PASS_ONLY",
            }[name]
            transitive.append({**row, "access": access, "hash_inherited_without_opening": True})

    primitive_order = [row["primitive_id"] for row in prior["primitive_role_assignment"]]
    qok = next(row for row in merges if row["merged"] == "qok")
    if int(qok["rank"]) != 7:
        raise SystemExit("qok rank drift")

    return {
        "schema": "gdt616-joint-child-feasible-binding-registration-v1",
        "experiment_id": "GDT616",
        "status": "REGISTERED_UNSCORED",
        "model_id": "HISTORICAL_MIXED_ABBREVIATION_FST_34_CORE_RUN_MACRO_V4_JOINT_CHILD_FEASIBLE",
        "created": "2026-08-29",
        "direct_input_hashes": source_rows,
        "transitive_partition_hashes_from_gdt615": transitive,
        "gdt615_import_policy": {
            "imported": [
                "primitive role assignment",
                "complete same-role primitive output deck",
                "paid output deck",
                "partition hashes and reveal order",
                "TRAIN substring relation",
                "inherited GDT614 downstream thresholds",
            ],
            "excluded": [
                "GDT615 Stage-0 selected mapping",
                "GDT615 mapping commit",
                "GDT615 raw-support objective",
                "GDT615 relaxed cover objective or witness",
            ],
            "terminal_prior_status": terminal["status"],
            "terminal_prior_use": "route rationale only; may not constrain X, Z, objectives, or candidates",
        },
        "inventory": {
            "merge_count": 64,
            "merge_rank_order": [row["merged"] for row in merges],
            "primitive_order": primitive_order,
            "primitive_role_assignment": prior["primitive_role_assignment"],
            "primitive_output_deck": prior["primitive_output_deck"],
            "paid_output_deck": prior["paid_output_deck"],
            "role_counts": model["role_counts"],
            "grammar": model["grammar"],
            "registered_transition_count": model["thresholds"]["registered_transitions"],
            "thresholds": model["thresholds"],
        },
        "train_substrings": {
            **prior["registered_train_substrings"],
            "recounted_distinct_entries": substring_count,
        },
        "variables": {
            "X": "same-role bijection from primitive IDs to complete primitive output-card tuples",
            "Z": "for each merge: NONE or one of eight named paid cards; each paid card exactly once",
            "actual_paid_locations": 8,
            "paid_short_cards": 4,
            "paid_macro_cards": 4,
            "relaxed_core_hit_variables": "FORBIDDEN",
        },
        "recursive_equations": {
            "primitive_effective": "eff(p)=output(X[p])",
            "merge_child": "child(m)=eff(left(m))||eff(right(m))",
            "merge_effective": "eff(m)=paid_output(Z[m]) if Z[m]!=NONE else child(m)",
            "order": "increasing merge rank; directed left then right",
        },
        "stage_a_fail_fast_hard_constraints": [
            "X is all-different inside each fixed role; card tuple metadata travels intact",
            "every paid card is used exactly once at eight distinct merge IDs",
            "child(m) is nonempty and in the registered TRAIN substring relation for every merge",
            "eff(m) is nonempty and in the registered TRAIN substring relation for every merge",
            "every paid output differs byte-for-byte from child(m)",
            "all 41 nonempty card outputs remain globally distinct",
            "merge rank 7 qok may not receive a paid macro card",
        ],
        "stage_a_selection": {
            "sat_freezes_mapping_or_paid_assignment": False,
            "stage_b_domain": "the complete Stage-A-feasible X+Z space",
            "diagnostic_witness_order": [
                "lexicographically minimize card IDs in registered primitive order",
                "lexicographically minimize ascending (merge rank, paid card ID) tuple",
            ],
            "diagnostic_witness_can_constrain_stage_b": False,
            "forbidden_objectives": [
                "raw train-substring support count",
                "relaxed paid-subtree cover minimum",
                "frequency",
                "lexicon or LM score",
                "distance from the GDT615 mapping",
            ],
        },
        "stage_b_integrated_w0": {
            "domain": "all Stage-A-feasible X+Z assignments plus complete TRAIN traces and tilings",
            "host_licenses": {
                "LEFT_HOST": "another non-NULL core term immediately left in the same CORE_RUN",
                "RIGHT_HOST": "another non-NULL core term immediately right in the same CORE_RUN",
                "STANDALONE_OR_LEFT_HOST": "singleton body term or LEFT_HOST",
                "non_hosts": ["PREFIX", "SUFFIX", "CONNECTOR", "NULL"],
            },
            "qok_paid_macro_forbidden": {"merge": "qok", "rank": 7, "longer_qok_family_implicitly_forbidden": False},
            "hard_constraints": [
                "complete GDT614 V2 grammar and 21 transitions",
                "ordered multiplicity-preserving span-bearing labelled traces",
                "nonoverlapping top-level 98-unit tilings",
                "34 primitive, eight paid, 56 default, eight paid-child, and all 64 merge labels",
                "registered train exposure, null-mass, collision, and focal-incidence-rank thresholds",
                "exact macro host licenses on labelled occurrences",
            ],
            "objective_hierarchy": [
                "maximize minimum distinct TRAIN-type exposure over all 42 cards",
                "maximize minimum direct TRAIN occurrence over the eight paid cards",
                "maximize total distinct labelled merge-node occurrences",
                "lexicographically minimize primitive card-ID sequence in registered primitive order",
                "lexicographically minimize ascending (merge rank, paid card ID) assignment tuple",
                "lexicographically minimize canonical complete trace/tiling serialization",
            ],
            "exact_optimality_required": True,
            "independent_replay_and_better-bound_exclusion_required": True,
        },
        "three_world_rule": {
            "worlds": ["W616_0", "W616_1", "W616_2"],
            "contrast_seed_starts": [61601, 61602],
            "seed_increment": 2,
            "attempt_limit_each": 10000,
            "permutation": "equal role and equal output length only",
            "minimum_primitive_assignment_differences": 24,
            "minimum_paid_location_or_output_differences": 6,
            "all_worlds_repeat_full_train_contract": True,
            "commit": "one hash-bound bundle before held or lm_confirm access",
        },
        "partition_access": {
            "pre_three_world_commit": ["merge DAG", "registered model/decks", "transitions", "units", "synthetic TRAIN", "TRAIN substrings", "lm_fit"],
            "synthetic_held": "open exactly once after complete three-world TRAIN bundle commit",
            "lm_confirm": "open only after three-world commit and held transfer pass",
            "voynich_target": "FORBIDDEN_THROUGHOUT_GDT616",
            "f84": "FORBIDDEN",
            "f84r": "FORBIDDEN",
        },
        "limits": {"workers_maximum": 32, "wall_clock_seconds_maximum": 43200, "unknown_or_timeout_can_pass": False},
        "outcomes": [
            "NO_JOINT_CHILD_FEASIBLE_BINDING",
            "JOINT_BOUND_PASS__W0_INFEASIBLE",
            "THREE_WORLD_GENERATOR_INFEASIBLE",
            "HELD_BINDING_NONTRANSFER",
            "SEARCH_INCOMPLETE",
            "OBJECTIVE_NON_IDENTIFYING",
            "OPTIMIZER_INSUFFICIENT",
            "SYNTHETIC_RECOVERY_PASS",
            "IMPLEMENTATION_OR_VALIDATION_FAILURE",
        ],
        "claim_ceiling": "synthetic Latin-carrier generator/recovery only; no Voynich unit, sound, word, language, plaintext, object, operation, or meaning",
        "canonical_artifact_policy": {
            "json": "UTF-8, indent=2, sorted keys, one terminal newline",
            "exclude": ["wall time", "worker order", "nondeterministic solver statistics", "transient work files"],
        },
    }


def canonical_bytes(payload: dict) -> bytes:
    return (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="verify the committed registration byte-for-byte")
    args = parser.parse_args()
    expected = canonical_bytes(build())
    if args.check:
        if not OUT.exists() or OUT.read_bytes() != expected:
            raise SystemExit("REGISTERED_SEARCH.json is absent or noncanonical")
        print(f"PASS {OUT.relative_to(ROOT)} sha256={hashlib.sha256(expected).hexdigest()}")
        return 0
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_bytes(expected)
    print(f"WROTE {OUT.relative_to(ROOT)} sha256={hashlib.sha256(expected).hexdigest()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
