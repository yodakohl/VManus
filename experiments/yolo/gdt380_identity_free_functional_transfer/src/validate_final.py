#!/usr/bin/env python3
"""Validate the bound GDT380 final stop artifact."""
from __future__ import annotations

import hashlib
import json
import csv
import gzip
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "experiments/yolo/gdt380_identity_free_functional_transfer"
ART = BASE / "artifacts"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def content(obj: dict) -> str:
    clone = dict(obj)
    clone.pop("content_hash", None)
    return hashlib.sha256(json.dumps(clone, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def main() -> None:
    result = json.loads((ART / "gdt380_result.json").read_text())
    checks = []

    def check(name: str, ok: bool) -> None:
        checks.append({"check": name, "pass": bool(ok)})
        if not ok:
            raise AssertionError(name)

    check("content_hash", result["content_hash"] == content(result))
    check("decision", result["status"] == "NO_IDENTITY_FREE_SIGNATURE_PASSED_COMPARATOR_GATE")
    check("zero_eligible", result["eligible_anonymous_families"] == [])
    check("target_not_run", result["voynich_target_stage"] == "NOT_AUTHORIZED_NOT_RUN" and result["voynich_target_rows_read"] == 0)
    check("f1_closed", result["f1"].startswith("CLOSED_FOR_SEMANTIC_INTERPRETATION"))
    check("f84_false", all(v is False for v in result["f84"].values()))
    # Reconstruct candidate mobility from the primary comparator inputs. This
    # explicitly guards against the GDT378 deterministic-slot null failure.
    obs_path = ROOT / "experiments/yolo/gdt378_cross_corpus_construction_transfer/artifacts/gdt378_comparator_observation_layer.tsv.gz"
    oracle_path = ROOT / "experiments/yolo/gdt378_cross_corpus_construction_transfer/artifacts/gdt378_hidden_oracle.tsv.gz"
    with gzip.open(obs_path, "rt", encoding="utf-8", newline="") as handle:
        obs = list(csv.DictReader(handle, delimiter="\t"))
    with gzip.open(oracle_path, "rt", encoding="utf-8", newline="") as handle:
        oracle = list(csv.DictReader(handle, delimiter="\t"))
    check("oracle_observation_alignment", [r["element_key"] for r in obs] == [r["element_key"] for r in oracle])
    strata = defaultdict(list)
    for i, row in enumerate(obs):
        n = int(row["record_element_count"])
        lb = "1-8" if n <= 8 else "9-16" if n <= 16 else "17-32" if n <= 32 else "33+"
        pb = min(4, int(float(row["relative_position"]) * 5))
        boundary = row["boundary_before"] + "|" + row["boundary_after"]
        frequency = int(row["within_record_frequency"])
        fb = "1" if frequency <= 1 else "2" if frequency == 2 else "3+"
        strata[(row["domain"], row["collection_id"], lb, pb, boundary, fb)].append(i)
    endpoints = {
        "CMP_FUNCTION_01": "UNTIL_STATE_GATE", "CMP_FUNCTION_02": "ALTERNATIVE_OR",
        "CMP_FUNCTION_03": "POLARITY_EXCLUSION", "CMP_FUNCTION_04": "FUNCTION_WORD",
    }
    with (ART / "gdt380_null_capacity.tsv").open(encoding="utf-8", newline="") as handle:
        capacity = {r["anonymous_family"]: r for r in csv.DictReader(handle, delimiter="\t")}
    for family, endpoint in endpoints.items():
        mixed = []
        for ids in strata.values():
            values = [int(oracle[i][endpoint]) for i in ids]
            if min(values) != max(values):
                mixed.append(ids)
        row = capacity[family]
        check(f"mobile_rows_{family}", sum(len(ids) for ids in mixed) == int(row["mobile_rows"]))
        check(f"mobile_strata_{family}", len(mixed) == int(row["mobile_strata"]) and len(mixed) > 0)
    for section in ["inputs", "documents", "implementation"]:
        for path, digest in result[section].items():
            check(section + "_" + path.replace("/", "_"), sha(ROOT / path) == digest)
    validation = {
        "schema": "GDT380_FINAL_VALIDATION_V1",
        "status": "PASS",
        "checks_passed": len(checks),
        "checks_total": len(checks),
        "checks": checks,
        "result_hash": sha(ART / "gdt380_result.json"),
        "comparator_validation_hash": sha(ART / "gdt380_comparator_validation.json"),
        "f84": {"opened": False, "parsed": False, "retained": False, "scored": False},
    }
    validation["content_hash"] = content(validation)
    (ART / "gdt380_validation.json").write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n")
    print(f"PASS {len(checks)}/{len(checks)}")


if __name__ == "__main__":
    main()
