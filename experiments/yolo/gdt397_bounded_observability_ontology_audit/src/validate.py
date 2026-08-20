#!/usr/bin/env python3
"""Independent structural validator for the compact GDT397 result."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt397_bounded_observability_ontology_audit"
G396 = ROOT / "experiments/yolo/gdt396_repaired_synthetic_identifiability_voynich_surface"
RESULT = EXP / "artifacts/gdt397_observability_results.tsv"
OUTPUT = EXP / "artifacts/gdt397_validation.json"

EXPECTED_FIELDS = (
    "row_type", "endpoint", "world", "surface", "model", "n", "n_positive",
    "metric_1", "value_1", "baseline_1", "metric_2", "value_2", "baseline_2",
    "metric_3", "value_3", "baseline_3", "strong_folds", "total_folds",
    "capacity", "decision", "observation_sha256", "interpretation_sha256",
    "details_json", "note",
)
DECISIONS = {
    "OBSERVABLE_AND_CURRENT_DECODER_LIMITED",
    "STRUCTURAL_ROLE_RECOVERABLE_SEMANTIC_LABEL_NOT_IDENTIFIABLE",
    "NOT_OBSERVABLE_UNDER_CURRENT_CHANNEL",
    "CAPACITY_INSUFFICIENT",
    "CURRENT_GDT396_RESULT_WAS_GATE_CONTAMINATION",
    "NONIDENTIFIABLE_BY_OBSERVATIONAL_EQUIVALENCE",
}
MODELED = {
    "LEXICAL_IDENTITY", "ANONYMOUS_CONTROL_ROLE", "REFERENCE_OR_REUSE_EDGE",
    "STATE_GATE_OR_SCOPE_ENDPOINT",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def content_hash(value: dict) -> str:
    clean = {key: item for key, item in value.items() if key != "content_sha256"}
    return hashlib.sha256(json.dumps(clean, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def main() -> int:
    if OUTPUT.exists():
        raise RuntimeError(f"refusing to overwrite {OUTPUT}")
    checks: dict[str, bool] = {}
    with RESULT.open(encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        rows = list(reader)
        checks["exact_header"] = tuple(reader.fieldnames or ()) == EXPECTED_FIELDS

    serialized = json.dumps(rows, sort_keys=True)
    checks["bounded_rows"] = 30 <= len(rows) <= 45
    checks["no_forbidden_seed_or_folio"] = "396200" not in serialized and "f84" not in serialized.lower()
    checks["registered_decisions_only"] = all(not row["decision"] or row["decision"] in DECISIONS for row in rows)
    checks["exact_ceiling_family"] = {
        (row["endpoint"], row["world"], row["surface"])
        for row in rows if row["row_type"] == "CEILING"
    } == {(endpoint, world, surface) for endpoint in MODELED for world in ("W02", "W09") for surface in ("FREE_RAW", "VOYNICH_RAW", "VOYNICH_ATOM_DECODED")}

    for endpoint in MODELED:
        for world in ("W02", "W09"):
            free = next(row for row in rows if row["row_type"] == "CEILING" and row["endpoint"] == endpoint and row["world"] == world and row["surface"] == "FREE_RAW")
            decoded = next(row for row in rows if row["row_type"] == "CEILING" and row["endpoint"] == endpoint and row["world"] == world and row["surface"] == "VOYNICH_ATOM_DECODED")
            compare = ("n", "n_positive", "metric_1", "value_1", "baseline_1", "metric_2", "value_2", "baseline_2", "metric_3", "value_3", "baseline_3", "strong_folds", "total_folds", "details_json")
            checks[f"atom_decode_restores_{endpoint}_{world}"] = all(free[key] == decoded[key] for key in compare)

    decisions = [row for row in rows if row["row_type"] == "ENDPOINT_DECISION"]
    checks["six_endpoint_decisions"] = len(decisions) == 6 and {row["endpoint"] for row in decisions} == MODELED | {"ALTERNATIVE_OR_BRANCH_TOPOLOGY", "REFERENTIAL_SEMANTICS"}
    checks["alternative_capacity_stop"] = next(row for row in decisions if row["endpoint"] == "ALTERNATIVE_OR_BRANCH_TOPOLOGY")["decision"] == "CAPACITY_INSUFFICIENT"
    checks["referential_equivalence_decision"] = next(row for row in decisions if row["endpoint"] == "REFERENTIAL_SEMANTICS")["decision"] == "NONIDENTIFIABLE_BY_OBSERVATIONAL_EQUIVALENCE"

    witness = [row for row in rows if row["row_type"] == "OBSERVATIONAL_EQUIVALENCE_WITNESS"]
    observation_path = G396 / ".work/corpora/qualification/W09/seed_3961000_free.tsv.gz"
    checks["witness_two_interpretations"] = len(witness) == 2 and {row["model"] for row in witness} == {"A_ORIGINAL_SEMANTIC_ORACLE", "B_FORMAL_ONLY"}
    checks["witness_identical_current_observation"] = len(witness) == 2 and len({row["observation_sha256"] for row in witness}) == 1 and witness[0]["observation_sha256"] == sha256(observation_path)
    checks["witness_distinct_interpretations"] = len(witness) == 2 and len({row["interpretation_sha256"] for row in witness}) == 2

    capacity = [row for row in rows if row["row_type"] == "CAPACITY" and row["endpoint"] == "ALTERNATIVE_OR_BRANCH_TOPOLOGY"]
    checks["alternative_two_world_capacity_rows"] = len(capacity) == 2 and {row["world"] for row in capacity} == {"W02", "W09"} and any(row["capacity"] == "INSUFFICIENT" for row in capacity)
    w10 = [row for row in rows if row["row_type"] == "W10_AUDIT"]
    checks["w10_formal_only_audit"] = len(w10) >= 4 and all(row["world"] == "W10" and not row["decision"] for row in w10)
    checks["w10_absent_edges_explicit"] = any(row["endpoint"] == "REFERENCE_OR_REUSE_EDGE" and row["capacity"] == "FORMAL_EDGE_ABSENT" for row in w10) and any(row["endpoint"] == "ALTERNATIVE_OR_BRANCH_TOPOLOGY" and row["capacity"] == "FORMAL_EDGE_ABSENT" for row in w10)

    hard = [row for row in rows if row["row_type"] == "HARD_STOP"]
    checks["one_hard_stop"] = len(hard) == 1
    if hard:
        detail = json.loads(hard[0]["details_json"])
        passing = detail["passing_operator_endpoints"]
        nominee = detail["single_future_nominee"]
        checks["hard_stop_consistent"] = (not passing and nominee == "NONE" and hard[0]["capacity"] == "STOP") or (passing and nominee in passing and hard[0]["capacity"] == "PASS")
    else:
        checks["hard_stop_consistent"] = False

    checks["gdt396_claim_freeze_still_present"] = (G396 / "artifacts/gdt396_qualification_claim_freeze.json").is_file()
    status = "PASS" if all(checks.values()) else "FAIL"
    output = {
        "schema": "GDT397_VALIDATION_V1",
        "status": status,
        "checks": checks,
        "passed": sum(checks.values()),
        "total": len(checks),
        "result_rows": len(rows),
        "result_sha256": sha256(RESULT),
        "method_sha256": sha256(EXP / "METHOD.md"),
        "runner_sha256": sha256(EXP / "src/run.py"),
        "validator_sha256": sha256(Path(__file__)),
        "f84": {"allowed": False, "accessed": False},
        "f84r": {"allowed": False, "accessed": False},
        "voynich_scored": False,
        "confirmation_seed_accessed": False,
    }
    output["content_sha256"] = content_hash(output)
    OUTPUT.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(OUTPUT, status, f"{output['passed']}/{output['total']}")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
