#!/usr/bin/env python3
"""Integrate and independently validate GDT615's terminal Stage-1 bound."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP_REL = Path("experiments/yolo/gdt615_joint_output_permutation_recovery")
EXP = ROOT / EXP_REL
STAGE1_REL = EXP_REL / "artifacts/stage1"
STAGE1 = ROOT / STAGE1_REL
MAPPING_REL = EXP_REL / "artifacts/stage0/STAGE0_MAPPING_COMMIT.json"
TREE_REL = Path("experiments/yolo/gdt608_compositional_stem_orientation/artifacts/merge_tree.tsv")
TRAIN_REL = EXP_REL / "artifacts/REGISTERED_TRAIN_SUBSTRINGS.txt"
TERMINAL_STATUS = "MAPPING_BOUND_PASS__FULL_WORLD_INFEASIBLE"
MAPPING_SHA256 = "edb909f41ced2c17e5b8cbe55189adb5736dc03b3893bfc6e6582c46b443a262"
UNSUPPORTED_RANKS = [14, 38, 45, 46, 47, 49, 53, 59, 60]
CORE_LABELS = [
    "E14_paid_requires_train_child_span",
    "U14_raw_unsupported_requires_paid_subtree",
]


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"JSON object required: {path}")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(value, indent=2, sort_keys=True) + "\n"
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(payload, encoding="utf-8")
    temporary.replace(path)


def read_tree() -> list[dict[str, str]]:
    with (ROOT / TREE_REL).open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if len(rows) != 64:
        raise AssertionError(f"expected 64 merges, found {len(rows)}")
    return rows


def reconstruct() -> dict[str, Any]:
    commit = load_json(ROOT / MAPPING_REL)
    mapping = {row["primitive_id"]: row["output"] for row in commit["mapping"]}
    if len(mapping) != 34:
        raise AssertionError("mapping does not contain 34 primitive IDs")
    train = set((ROOT / TRAIN_REL).read_text(encoding="ascii").splitlines())
    render = dict(mapping)
    descendants: dict[str, set[int]] = {primitive: set() for primitive in mapping}
    merges: list[dict[str, Any]] = []
    for expected_rank, row in enumerate(read_tree(), 1):
        rank = int(row["rank"])
        if rank != expected_rank or row["left"] not in render or row["right"] not in render:
            raise AssertionError(f"bad topological merge row {expected_rank}")
        name = row["merged"]
        raw = render[row["left"]] + render[row["right"]]
        subtree = {rank} | descendants[row["left"]] | descendants[row["right"]]
        render[name] = raw
        descendants[name] = subtree
        merges.append(
            {
                "rank": rank,
                "merge": name,
                "left": row["left"],
                "right": row["right"],
                "raw_render": raw,
                "train_supported": raw in train,
                "inclusive_subtree_ranks": sorted(subtree),
            }
        )
    return {"mapping": mapping, "merges": merges, "train": train}


def file_row(relative: Path) -> dict[str, Any]:
    path = ROOT / relative
    return {"path": relative.as_posix(), "bytes": path.stat().st_size, "sha256": digest(path)}


def main(argv: list[str] | None = None) -> int:
    del argv
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, detail: Any = "") -> None:
        checks.append({"check": name, "pass": bool(condition), "detail": str(detail)})
        if not condition:
            raise AssertionError(f"{name}: {detail}")

    manifest = load_json(EXP / "experiment.json")
    primary_rel = STAGE1_REL / "PRIMARY_RESULT.json"
    independent_rel = STAGE1_REL / "INDEPENDENT_RESULT.json"
    contract_rel = STAGE1_REL / "CONTRACT_AUDIT.json"
    primary = load_json(ROOT / primary_rel)
    independent = load_json(ROOT / independent_rel)
    contract = load_json(ROOT / contract_rel)
    replay = reconstruct()
    merges = replay["merges"]
    unsupported = [row for row in merges if not row["train_supported"]]
    rank14 = merges[13]

    check("experiment_id", manifest.get("experiment_id") == "GDT615")
    check("terminal_manifest_status", manifest.get("status") == TERMINAL_STATUS, manifest.get("status"))
    check("sealed_f84", manifest.get("sealed_data", {}).get("f84") == "FORBIDDEN")
    check("sealed_f84r", manifest.get("sealed_data", {}).get("f84r") == "FORBIDDEN")
    check("mapping_commit_hash", digest(ROOT / MAPPING_REL) == MAPPING_SHA256)
    check("train_table_hash", digest(ROOT / TRAIN_REL) == "5b6859d8656f63cf8e8cf89221ae8ff1dea345e135a6cd012248b9b4c4ff14a9")
    check("merge_tree_hash", digest(ROOT / TREE_REL) == "2098c71be9da13b483cf2561e06412276d8c60aa32e72520e8877f8f5d53090a")
    check("raw_support_55", sum(row["train_supported"] for row in merges) == 55)
    check("unsupported_ranks", [row["rank"] for row in unsupported] == UNSUPPORTED_RANKS)
    check("ey_identity", (rank14["merge"], rank14["left"], rank14["right"]) == ("Ey", "E", "y"))
    check("ey_mapping", replay["mapping"]["E"] == "ho" and replay["mapping"]["y"] == "i")
    check("ey_raw_render", rank14["raw_render"] == "hoi")
    check("ey_train_absent", "hoi" not in replay["train"])
    check("ey_singleton_subtree", rank14["inclusive_subtree_ranks"] == [14])

    check("primary_schema", primary.get("schema") == "gdt615-stage1-primary-child-counterpart-bound-v1")
    check("primary_unsat", primary.get("status") == "UNSAT" and primary.get("solver", {}).get("result") == "UNSAT")
    check("primary_decision", primary.get("decision") == "NECESSARY_CHILD_COUNTERPART_BOUND_UNSAT")
    check("primary_mapping_hash", primary.get("mapping_commit_sha256") == MAPPING_SHA256)
    check("primary_exact_eight", primary.get("bound", {}).get("paid_merge_location_count_exact") == 8)
    check("primary_eligible_55", primary.get("bound", {}).get("eligible_paid_location_count") == 55)
    check("primary_unsupported", [row["rank"] for row in primary.get("bound", {}).get("raw_unsupported_merges", [])] == UNSUPPORTED_RANKS)
    core = primary.get("query_core_certificate", {})
    check("primary_core", core.get("minimal_unsat_core_labels") == CORE_LABELS)
    check("primary_core_subset_minimal", core.get("core_subset_minimal") is True)
    check("primary_core_drop_replays_sat", [row.get("result") for row in core.get("core_minimality_replays", [])] == ["SAT", "SAT"])
    primary_access = primary.get("partition_access", {})
    check(
        "primary_no_later_data",
        primary_access.get("train_substring_table_opened") is True
        and not primary_access.get("confirmation_lm_opened")
        and not primary_access.get("held_opened")
        and not primary_access.get("sealed_folio_data_opened")
        and not primary_access.get("voynich_target_opened"),
    )

    check("independent_schema", independent.get("schema") == "gdt615-stage1-independent-child-counterpart-bound-v1")
    indep_decision = independent.get("decision", {})
    check("independent_unsat", indep_decision.get("status") == "STAGE1_TRAIN_CHILD_COUNTERPART_INFEASIBLE")
    check("independent_no_exact_eight", indep_decision.get("exact_eight_paid_set_exists") is False)
    check("independent_contradiction", independent.get("proof", {}).get("contradiction_ranks") == [14])
    structural = independent.get("proof", {}).get("structural_cover_without_counterpart_gate", {})
    check("independent_stage0_cover", structural.get("minimum") == 4 and structural.get("lex_ranks") == [2, 3, 14, 23])
    overbound = independent.get("proof", {}).get("counterpart_over_relaxation", {})
    check("independent_overrelaxation_unsat", overbound.get("feasible_within_limit") is False)
    scope = independent.get("scope", {})
    check("independent_train_only", scope.get("train_only") is True)
    check("independent_no_later_data", not scope.get("held_or_lm_confirm_opened") and not scope.get("target_or_voynich_data_opened") and not scope.get("f84_or_f84r_opened"))

    check("contract_schema", contract.get("schema") == "gdt615-stage1-contract-necessary-bound-audit-v1")
    check("contract_pass", contract.get("status") == "PASS")
    check("contract_decision", contract.get("decision") == "CONTRACT_NECESSARY_BOUND_PROVES_W0_INFEASIBLE")
    witnesses = contract.get("minimal_witnesses", [])
    check("contract_single_witness", len(witnesses) == 1 and witnesses[0].get("rank") == 14)
    check("contract_witness_render", witnesses[0].get("raw_unoverridden_child_composition") == "hoi")
    check("contract_witness_subtree", witnesses[0].get("inclusive_recursive_merge_subtree_ranks") == [14])
    check("contract_two_cases_complete", witnesses[0].get("paid_or_default_case_partition_is_complete") is True)
    check("contract_clauses_present", all(row.get("present") for row in contract.get("contract_clause_evidence", [])))
    access = contract.get("input_access", {})
    check("contract_no_later_data", not access.get("held_opened") and not access.get("lm_confirm_opened") and not access.get("voynich_target_opened") and not access.get("f84_opened") and not access.get("f84r_opened"))

    # The contradiction is a two-clause logical certificate: coverage of the
    # unsupported singleton subtree forces paid[14], while direct exposure of
    # the registered child composition forbids paid[14]. Exact cardinality,
    # card roles, grammar, and tiling can only remove more assignments.
    check("direct_coverage_forces_paid14", not rank14["train_supported"] and rank14["inclusive_subtree_ranks"] == [14])
    check("direct_counterpart_forbids_paid14", rank14["raw_render"] not in replay["train"])

    evidence_rows = [file_row(primary_rel), file_row(independent_rel), file_row(contract_rel)]
    terminal = {
        "schema": "gdt615-stage1-terminal-result-v1",
        "status": TERMINAL_STATUS,
        "stage0_mapping_commit_sha256": MAPPING_SHA256,
        "decision": {
            "full_train_world_exists_under_registered_contract": False,
            "reason": "The registered Stage-1 train world fails a strictly more permissive necessary bound.",
            "registered_stop_outcome": TERMINAL_STATUS,
        },
        "minimal_unsat_core": {
            "merge": "Ey",
            "rank": 14,
            "left_child": "E",
            "left_output": "ho",
            "right_child": "y",
            "right_output": "i",
            "unoverridden_child_composition": "hoi",
            "train_substring_member": False,
            "inclusive_recursive_merge_subtree_ranks": [14],
            "coverage_consequence": "rank 14 must be an actual paid location",
            "paid_child_consequence": "rank 14 cannot be an actual paid location",
            "primary_core_labels": CORE_LABELS,
        },
        "necessary_bound": {
            "merge_count": 64,
            "raw_supported_count": 55,
            "raw_unsupported_count": 9,
            "raw_unsupported_ranks": UNSUPPORTED_RANKS,
            "actual_paid_location_count_required": 8,
            "child_counterpart_eligible_location_count": 55,
            "solver_result": "UNSAT",
            "omitted_constraints": [
                "four-short/four-macro assignment",
                "paid output inequality and side licenses",
                "V2 grammar and 21 transitions",
                "ordered span-bearing traces",
                "nonoverlapping 98-unit tilings",
                "train exposure objectives",
            ],
        },
        "independent_agreement": {
            "implementations": 3,
            "primary_z3": "UNSAT with subset-minimal two-clause core",
            "independent_combinatorial": "UNSAT in a larger admitted assignment space",
            "contract_two_case_audit": "paid and default branches both impossible",
            "evidence": evidence_rows,
        },
        "execution_stop": {
            "actual_paid_locations_selected": False,
            "paid_cards_assigned": False,
            "w0_constructed": False,
            "w1_or_w2_constructed": False,
            "held_opened": False,
            "lm_confirm_opened": False,
            "oracle_run": False,
            "recovery_run": False,
            "next_best_stage0_mapping_tried": False,
        },
        "claim_ceiling": "Terminal result for the synthetic Latin-carrier truth generator only. No Voynich unit, sound, language, word, plaintext, object, operation, or meaning is assigned.",
        "f84_or_f84r_opened": False,
        "voynich_target_opened": False,
    }
    terminal_rel = STAGE1_REL / "STAGE1_RESULT.json"
    write_json(ROOT / terminal_rel, terminal)

    bundle_files = [
        primary_rel,
        independent_rel,
        contract_rel,
        terminal_rel,
        EXP_REL / "src/stage1/primary_bound.py",
        EXP_REL / "src/stage1/test_primary_bound.py",
        EXP_REL / "src/stage1/independent_bound.py",
        EXP_REL / "src/stage1/contract_audit.py",
        EXP_REL / "src/stage1/test_contract_audit.py",
        EXP_REL / "src/stage1_validate.py",
    ]
    bundle = {
        "schema": "gdt615-stage1-terminal-bundle-v1",
        "status": TERMINAL_STATUS,
        "files": [file_row(path) for path in bundle_files],
        "excluded_as_not_run": ["W0", "W1", "W2", "held", "lm_confirm", "oracle", "recovery"],
        "transient_work_directories_excluded": True,
    }
    bundle_rel = STAGE1_REL / "STAGE1_BUNDLE.json"
    write_json(ROOT / bundle_rel, bundle)

    for row in bundle["files"]:
        check(f"bundle_{Path(row['path']).name}", digest(ROOT / row["path"]) == row["sha256"])

    validation = {
        "schema": "gdt615-stage1-terminal-validation-v1",
        "status": "PASS",
        "registered_outcome": TERMINAL_STATUS,
        "checks_total": len(checks),
        "checks_passed": sum(bool(row["pass"]) for row in checks),
        "checks": checks,
        "stage0_mapping_commit_sha256": MAPPING_SHA256,
        "terminal_result_sha256": digest(ROOT / terminal_rel),
        "bundle_sha256": digest(ROOT / bundle_rel),
        "held_or_lm_confirm_opened": False,
        "voynich_target_opened": False,
        "f84_or_f84r_opened": False,
    }
    validation_rel = STAGE1_REL / "STAGE1_VALIDATION.json"
    write_json(ROOT / validation_rel, validation)
    print(f"STAGE1_TERMINAL_VALIDATION_PASS {validation['checks_passed']}/{validation['checks_total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
