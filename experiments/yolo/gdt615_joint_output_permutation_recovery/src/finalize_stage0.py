#!/usr/bin/env python3
"""Build the deterministic public GDT615 Stage-0 certificate bundle.

This finalizer reads only the three registered Stage-0 inputs, already-frozen
solver outputs, and two byte-stability run directories.  It never opens held,
LM-confirm, Voynich target, f84, or f84r material.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve()
ROOT = next(parent for parent in HERE.parents if (parent / ".git").is_dir())
EXP = ROOT / "experiments/yolo/gdt615_joint_output_permutation_recovery"
ART = EXP / "artifacts/stage0"

STABLE_PRIMARY_FILES = (
    "BASE_ENCODING.smt2",
    "INPUT_MANIFEST.json",
    "QUERY_CERTIFICATES.jsonl",
    "RESULT.json",
    "RESULT.sha256",
    "COMPLETE.json",
    "mapping.tsv",
    "minimum_cover.tsv",
    "raw_merges.tsv",
)

PUBLIC_PRIMARY_NAMES = {
    "BASE_ENCODING.smt2": "PRIMARY_BASE_ENCODING.smt2",
    "INPUT_MANIFEST.json": "PRIMARY_INPUT_MANIFEST.json",
    "QUERY_CERTIFICATES.jsonl": "PRIMARY_QUERY_CERTIFICATES.jsonl",
    "RESULT.json": "PRIMARY_RESULT.json",
    "mapping.tsv": "mapping.tsv",
    "minimum_cover.tsv": "minimum_cover.tsv",
    "raw_merges.tsv": "raw_merges.tsv",
}


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def publish_json(path: Path, value: Any) -> None:
    payload = canonical_bytes(value)
    if path.exists():
        if path.read_bytes() != payload:
            raise RuntimeError(f"refusing to replace nonidentical certificate: {path}")
        return
    path.write_bytes(payload)


def public_path(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def load_query_records(path: Path) -> dict[str, dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        query_id = row["query_id"]
        if query_id in records:
            raise RuntimeError(f"duplicate query ID: {query_id}")
        records[query_id] = row
    if len(records) != 193:
        raise RuntimeError(f"expected 193 query records, found {len(records)}")
    return records


def decisive_queries(records: dict[str, dict[str, Any]]) -> dict[str, Any]:
    base = [
        "same-role card-to-primitive bijection over all 34 slots",
        "exact registered train-substring MDD membership for all 64 raw renders",
        "for each unsupported render, at least one hit in its inclusive merge subtree",
        "at most 8 merge-node hits",
    ]
    key = [
        "N01", "Y03", "K01", "S03", "L02", "Y01", "L03", "P01",
        "K02", "L01", "L05", "Y02", "L09", "L16", "L06", "P02",
        "L08", "C01", "L10", "L13", "C02", "S01", "M01", "L04",
        "L11", "L12", "Y04", "L15", "L14", "S02", "L17", "P03",
        "L07", "L18",
    ]
    specifications = (
        ("Q0001", "existence", "sat", base),
        ("Q0006", "support_55_exists", "sat", base + ["support >= 55"]),
        ("Q0007", "support_56_excluded", "unsat", base + ["support >= 56"]),
        ("Q0011", "cover_4_exists_at_support_55", "sat", base + ["support = 55", "hit count <= 4"]),
        ("Q0012", "cover_3_excluded_at_support_55", "unsat", base + ["support = 55", "hit count <= 3"]),
        ("Q0190", "final_key_exists", "sat", base + ["support = 55", "hit count <= 4", f"card-ID key = {key}"]),
        ("Q0191", "earlier_key_excluded", "unsat", base + ["support = 55", "hit count <= 4", f"card-ID key lexicographically precedes {key}"]),
        ("Q0192", "canonical_cover_exists", "sat", base + ["support = 55", "hit count = 4", f"card-ID key = {key}", "ascending cover tuple = [2, 3, 14, 23]"]),
        ("Q0193", "earlier_cover_excluded", "unsat", base + ["support = 55", "hit count = 4", f"card-ID key = {key}", "ascending cover tuple lexicographically precedes [2, 3, 14, 23]"]),
    )
    rows = []
    for query_id, claim, expected, context in specifications:
        record = records.get(query_id)
        if record is None or record.get("result") != expected:
            raise RuntimeError(f"decisive query mismatch: {query_id}")
        rows.append(
            {
                "claim": claim,
                "effective_context": context,
                "logged_constraint": record["constraint"],
                "phase": record["phase"],
                "query_id": query_id,
                "result": record["result"],
            }
        )
    return {
        "schema": "gdt615-stage0-decisive-query-contexts-v1",
        "status": "PASS",
        "base_encoding_sha256": digest(ART / "PRIMARY_BASE_ENCODING.smt2"),
        "full_query_log_sha256": digest(ART / "PRIMARY_QUERY_CERTIFICATES.jsonl"),
        "note": "The JSONL records the delta for each query; effective_context records the complete accumulated formula used for the decisive boundary checks.",
        "queries": rows,
    }


def compare_solver_results(primary: dict[str, Any], independent: dict[str, Any]) -> None:
    if primary.get("decision") != "STAGE0_MAPPING_BOUND_PASS":
        raise RuntimeError("primary Stage-0 decision is not a mapping-bound pass")
    if independent.get("status") != "GLOBAL_OPTIMUM_COMPLETE" or not independent.get("complete"):
        raise RuntimeError("independent full-space search is incomplete")
    primary_objective = primary["objective"]
    independent_objective = independent["objective"]
    if primary_objective["raw_train_supported_named_merges"] != independent_objective["raw_supported_merge_count"]:
        raise RuntimeError("solver support optima disagree")
    if primary_objective["exact_minimum_core_hit"] != independent_objective["minimum_inclusive_dag_cover"]:
        raise RuntimeError("solver cover optima disagree")
    primary_mapping = [
        (row["primitive_id"], row["role"], row["card_id"], row["output"])
        for row in primary["mapping"]
    ]
    independent_mapping = [
        (row["primitive_id"], row["role"], row["card_id"], row["output"])
        for row in independent["mapping"]
    ]
    if primary_mapping != independent_mapping:
        raise RuntimeError("solver mappings disagree")
    primary_supported = [
        row["rank"] for row in primary["raw_merges"] if row["train_substring_member"]
    ]
    if primary_supported != independent["supported_merge_ranks"]:
        raise RuntimeError("solver supported-rank sets disagree")
    primary_cover = [row["rank"] for row in primary["canonical_minimum_cover"]]
    if primary_cover != independent["minimum_cover_ranks"]:
        raise RuntimeError("solver canonical covers disagree")
    if not independent.get("winner_direct_replay_matches"):
        raise RuntimeError("independent winner direct replay failed")
    control = independent["negative_control"]
    if not control.get("matches_registered_expectation"):
        raise RuntimeError("independent negative control failed")
    if (
        control["raw_supported_merge_count"]
        != primary["negative_control"]["replayed_raw_supported_merges"]
        or control["minimum_inclusive_dag_cover"]
        != primary["negative_control"]["replayed_exact_minimum"]
    ):
        raise RuntimeError("solver negative controls disagree")


def build_mapping_commit(primary: dict[str, Any], independent: dict[str, Any]) -> dict[str, Any]:
    unsupported = [
        {
            "merge": row["merge"],
            "rank": row["rank"],
            "raw_render": row["raw_render"],
        }
        for row in primary["raw_merges"]
        if not row["train_substring_member"]
    ]
    return {
        "schema": "gdt615-stage0-mapping-commit-v1",
        "status": "STAGE0_MAPPING_CERTIFICATE_PASS__STAGE1_NOT_RUN",
        "claim_scope": "Synthetic Latin-carrier train-only same-role binding and permissive necessary merge-subtree bound; no Voynich reading, plaintext, object, operation, or meaning is assigned.",
        "held_or_lm_confirm_opened": False,
        "voynich_target_opened": False,
        "f84_or_f84r_opened": False,
        "registered_input_sha256": primary["input_hashes"],
        "objective": primary["objective"],
        "mapping": primary["mapping"],
        "raw_supported_merge_ranks": [
            row["rank"] for row in primary["raw_merges"] if row["train_substring_member"]
        ],
        "raw_unsupported_merges": unsupported,
        "canonical_relaxed_minimum_cover": primary["canonical_minimum_cover"],
        "negative_control": primary["negative_control"],
        "exact_evidence": {
            "primary_result_sha256": digest(ART / "PRIMARY_RESULT.json"),
            "primary_query_log_sha256": digest(ART / "PRIMARY_QUERY_CERTIFICATES.jsonl"),
            "independent_result_sha256": digest(ART / "INDEPENDENT_RESULT.json"),
            "primary_and_independent_full_mapping_match": True,
            "primary_and_independent_supported_rank_set_match": True,
            "primary_and_independent_objectives_match": True,
            "primary_and_independent_canonical_cover_match": True,
            "independent_full_space_tasks_completed": independent["search"]["small_role_tasks_completed"],
            "independent_full_space_tasks_total": independent["search"]["small_role_tasks_total"],
        },
        "stage0_cover_is_actual_paid_location_selection": False,
        "stage1_status": "NOT_RUN",
        "next_immutable_step": "Use this exact mapping hash to construct and commit W0, W1, and W2 plus each world's eight actual train-only paid locations before a single held reveal.",
    }


def build_replay_certificate(primary_run: Path, primary_replay: Path) -> dict[str, Any]:
    hashes: dict[str, dict[str, Any]] = {}
    for name in STABLE_PRIMARY_FILES:
        first = digest(primary_run / name)
        second = digest(primary_replay / name)
        if first != second:
            raise RuntimeError(f"primary stable replay mismatch: {name}")
        hashes[name] = {
            "first_sha256": first,
            "replay_sha256": second,
            "byte_identical": True,
        }
        public_name = PUBLIC_PRIMARY_NAMES.get(name)
        if public_name and digest(ART / public_name) != first:
            raise RuntimeError(f"published primary copy mismatch: {public_name}")
    return {
        "schema": "gdt615-stage0-primary-replay-certificate-v1",
        "status": "PASS",
        "stable_files": hashes,
        "excluded_volatile_files": ["QUERY_DIAGNOSTICS.jsonl"],
        "stale_pid_run_state_published": False,
    }


def build_bundle() -> dict[str, Any]:
    paths = (
        ART / "PRIMARY_BASE_ENCODING.smt2",
        ART / "PRIMARY_INPUT_MANIFEST.json",
        ART / "PRIMARY_QUERY_CERTIFICATES.jsonl",
        ART / "PRIMARY_RESULT.json",
        ART / "INDEPENDENT_RESULT.json",
        ART / "mapping.tsv",
        ART / "raw_merges.tsv",
        ART / "minimum_cover.tsv",
        ART / "DECISIVE_QUERY_MANIFEST.json",
        ART / "STAGE0_MAPPING_COMMIT.json",
        ART / "STAGE0_REPLAY_CERTIFICATE.json",
        EXP / "src/primary/solve.py",
        EXP / "src/primary/test_solve.py",
        EXP / "src/independent/stage0_independent.cpp",
        EXP / "src/independent/Makefile",
        HERE,
    )
    return {
        "schema": "gdt615-stage0-stable-bundle-v1",
        "status": "PASS",
        "files": [
            {"path": public_path(path), "sha256": digest(path), "bytes": path.stat().st_size}
            for path in paths
        ],
        "volatile_files_excluded": [
            "QUERY_DIAGNOSTICS.jsonl",
            "RUN_STATE.json",
            "compiler binaries",
            "temporary work directories",
        ],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--primary-run", type=Path, required=True)
    parser.add_argument("--primary-replay", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    primary_run = args.primary_run.resolve()
    primary_replay = args.primary_replay.resolve()
    primary = load_json(ART / "PRIMARY_RESULT.json")
    independent = load_json(ART / "INDEPENDENT_RESULT.json")
    compare_solver_results(primary, independent)

    records = load_query_records(ART / "PRIMARY_QUERY_CERTIFICATES.jsonl")
    publish_json(ART / "DECISIVE_QUERY_MANIFEST.json", decisive_queries(records))
    publish_json(ART / "STAGE0_MAPPING_COMMIT.json", build_mapping_commit(primary, independent))
    publish_json(
        ART / "STAGE0_REPLAY_CERTIFICATE.json",
        build_replay_certificate(primary_run, primary_replay),
    )
    publish_json(ART / "STAGE0_BUNDLE.json", build_bundle())
    print("STAGE0_FINALIZE_PASS support=55 cover=4 mapping=34/34")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
