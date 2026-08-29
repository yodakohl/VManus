#!/usr/bin/env python3
"""Replay one heuristic scout candidate's registered train-side structure."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from scout_core import (
    CLAIM,
    ROOT,
    canonical_json,
    load_problem,
    mapping_from_candidate,
    require_work_path,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("candidate", type=Path)
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="optional JSON path below artifacts/stage0_scout_work",
    )
    return parser.parse_args()


def replay(candidate_path: Path) -> dict[str, object]:
    candidate_path = require_work_path(
        candidate_path,
        allow_scout_source=True,
        allow_public_candidate=True,
    )
    payload = json.loads(candidate_path.read_text(encoding="utf-8"))
    if payload.get("claim") != CLAIM or payload.get("scientific_pass") is not False:
        raise ValueError("candidate does not carry the mandatory scout-only claim")
    problem = load_problem()
    mapping = problem.validate_mapping(mapping_from_candidate(payload))
    evaluation = problem.evaluate(mapping)
    cover = problem.canonical_cover(evaluation.supported_mask)

    checks = {
        "candidate_claim_is_scout_only": True,
        "registered_input_hashes_match": payload.get("registered_input_hashes")
        == problem.input_hashes,
        "mapping_is_rolewise_bijection": True,
        "raw_support_count_matches": payload.get(
            "raw_train_supported_merge_count"
        )
        == evaluation.support_count,
        "candidate_local_cover_minimum_matches": payload.get(
            "candidate_local_exact_cover_minimum"
        )
        == evaluation.cover_minimum,
        "canonical_cover_matches": payload.get(
            "candidate_local_canonical_cover_ranks"
        )
        == list(cover),
        "all_raw_merge_rows_match": payload.get("raw_merges")
        == problem.candidate_payload(
            evaluation, provenance=payload.get("provenance", {})
        )["raw_merges"],
    }
    passed = all(checks.values())
    result = {
        "schema": "gdt615-stage0-scout-candidate-structural-replay-v1",
        "claim": CLAIM,
        "scientific_pass": False,
        "global_optimality_checked": False,
        "candidate_path": candidate_path.relative_to(ROOT).as_posix(),
        "candidate_id": payload.get("candidate_id"),
        "status": "STRUCTURAL_REPLAY_OK" if passed else "STRUCTURAL_REPLAY_MISMATCH",
        "raw_train_supported_merge_count": evaluation.support_count,
        "candidate_local_exact_cover_minimum": evaluation.cover_minimum,
        "candidate_local_canonical_cover_ranks": list(cover),
        "checks": checks,
    }
    if not passed:
        raise AssertionError(canonical_json(result))
    return result


def main() -> int:
    args = parse_args()
    result = replay(args.candidate)
    rendered = canonical_json(result)
    if args.output is not None:
        output = require_work_path(args.output)
        if output.exists():
            raise FileExistsError(f"refusing to overwrite replay output: {output}")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
