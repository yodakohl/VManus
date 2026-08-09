#!/usr/bin/env python3
"""Reproduce and localize the v1 unsigned cyclic-rotation defect."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

import numpy as np

from cho_che_scope_core import load_panels, rotated_batch, stable_u64, synthetic_labels


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
MASKED = RESULTS / "cho_che_scope_masked_events.tsv"
SPEC = BASE / "CHO_CHE_SCOPE_SYNTHETIC_PREFLIGHT_SPEC.md"
CORE = BASE / "cho_che_scope_core.py"
RUNNER = BASE / "run_cho_che_scope_synthetic_preflight.py"
PREFLIGHT = RESULTS / "cho_che_scope_synthetic_preflight.json"
PREFLIGHT_REPORT = RESULTS / "cho_che_scope_synthetic_preflight_report.md"
AUDITOR = Path(__file__).resolve()
OUT = RESULTS / "cho_che_scope_rotation_v1_audit.json"
REPORT = RESULTS / "cho_che_scope_rotation_v1_audit_report.md"
TARGET_OUT = RESULTS / "cho_che_scope_target.json"
TARGET_REPORT = RESULTS / "cho_che_scope_target_report.md"

HASHES = {
    MASKED: "41f8b517419d2215a97db9ce245c5639f383b11c41d8c1377a245dea8e37abf3",
    SPEC: "b2b51a91b999ae926170a76ce8ffe8f5b8a7d01f3e71200e93b26cefce900c94",
    CORE: "fc57f5b96ea49fc380aabc1fbed81273111a6d3981f1fd46bbbb0aeff05891e4",
    RUNNER: "dba9ae5182ad9f8b8e036d9e1b367b8440475b644c776bffe5e277f9daa6f088",
    PREFLIGHT: "203ab1e60c83f43f6cb095b095c461cf7742ba30fecf6ff0cc2b79925c82331e",
    PREFLIGHT_REPORT: "59817e4f422307e1a5361de2aaea96febe7137ffd279b2e4da26ac53ffc658d6",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing to overwrite v1 rotation audit")
    for path, expected in HASHES.items():
        if sha(path) != expected:
            raise SystemExit(f"hash mismatch: {path.name}")
    preflight = json.loads(PREFLIGHT.read_text())
    if preflight["status"] != "STOP_SCOPE_PREFLIGHT_FAILED_TARGET_FORBIDDEN":
        raise ValueError("v1 preflight did not stop")
    panel = load_panels(MASKED)["ZL3b"]
    labels = synthetic_labels(panel, 0, "PARAGRAPH", 2.0)
    assignments = np.arange(1, 17, dtype=np.uint64)
    violations = []
    for ensemble in ("INDEPENDENT_STRATUM", "COUPLED_PAGE"):
        rotated = rotated_batch(panel, labels, assignments, ensemble, "CHO_CHE_SCOPE_MULTISET")
        for stratum_index, (positions, page, key) in enumerate(panel.rotation_strata):
            expected = int(labels[positions].sum())
            observed = rotated[:, positions].sum(axis=1)
            for assignment_index in np.flatnonzero(observed != expected):
                violations.append({
                    "ensemble": ensemble,
                    "assignment": int(assignments[assignment_index]),
                    "stratum_index": stratum_index,
                    "stratum_size": len(positions),
                    "expected_ones": expected,
                    "observed_ones": int(observed[assignment_index]),
                })
    if not violations:
        raise ValueError("failed to reproduce rotation defect")

    first = violations[0]
    positions = panel.rotation_strata[first["stratum_index"]][0]
    n = len(positions)
    # The v1 expression subtracts unsigned integers before modulo n. When
    # j<shift, it computes (2^64+j-shift) mod n instead of (j-shift) mod n.
    differs_for_some_shift = any(
        [((j - shift) & ((1 << 64) - 1)) % n for j in range(n)]
        != [(j + n - shift) % n for j in range(n)]
        for shift in range(1, n)
    )
    result = {
        "experiment": "CHO_CHE_SCOPE_ROTATION_V1_AUDIT",
        "status": "CONFIRMED_UNSIGNED_UNDERFLOW_INVALIDATES_V1_ROTATIONS",
        "inputs": {path.name: sha(path) for path in (*HASHES, AUDITOR)},
        "violations_in_16_assignments": len(violations),
        "first_violation": first,
        "unsigned_and_mathematical_modulo_differ": differs_for_some_shift,
        "failed_gate": "rotation_multiset_preservation",
        "v1_scores_valid": False,
        "target_outputs_absent": not TARGET_OUT.exists() and not TARGET_REPORT.exists(),
        "target_outcomes_accessed": 0,
        "target_scores_computed": 0,
        "repair": "compute (j+n-shift) mod n before array indexing, version all hashes, rerun synthetic controls only",
        "claim_ceiling": "Implementation correction only; no manuscript outcome, scope, meaning, plaintext, or translation follows.",
    }
    if not result["target_outputs_absent"] or not differs_for_some_shift:
        raise ValueError("audit safety gate failure")
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    REPORT.write_text(f"""# `cho/che` scope preflight v1 rotation audit

Status: **{result['status']}**

The frozen multiset control found **{len(violations)}** violations in the first
16 assignments. V1 subtracts unsigned indices before taking modulo `n`; when
the subtraction is negative it wraps at `2^64`, so some rows duplicate one
source position and omit another. The first failure is assignment
**{first['assignment']}**, {first['ensemble']} stratum **{first['stratum_index']}**
of size **{first['stratum_size']}**, with **{first['observed_ones']}** observed
ones instead of **{first['expected_ones']}**.

All v1 null and power scores are invalid and confer no target authorization.
The target remained absent and zero manuscript outcomes or scores were opened.
The only admissible repair is a versioned `(j+n-shift) mod n` implementation
followed by a synthetic-only rerun under unchanged scientific gates.
""")
    print(json.dumps({"status": result["status"], "violations": len(violations), "target_absent": result["target_outputs_absent"]}, sort_keys=True))


if __name__ == "__main__":
    main()
