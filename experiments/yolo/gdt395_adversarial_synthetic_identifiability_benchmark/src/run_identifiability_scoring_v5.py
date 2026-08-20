#!/usr/bin/env python3
"""Reproduce the conformed GDT395 aggregate score from frozen bindings."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

import score_identifiability_v5 as scorer

ROOT = Path(__file__).resolve().parents[4]
EXP = ROOT / "experiments/yolo/gdt395_adversarial_synthetic_identifiability_benchmark"


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_hash(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
    ).encode("ascii")).hexdigest()


def require_correction_lineage() -> None:
    freeze_path = EXP / "artifacts/gdt395_scorer_validator_conformance_v5.json"
    validation_path = EXP / "artifacts/gdt395_scorer_validator_conformance_v5_validation.json"
    freeze = json.loads(freeze_path.read_text())
    validation = json.loads(validation_path.read_text())
    freeze_payload = dict(freeze)
    freeze_declared = freeze_payload.pop("content_sha256", "")
    validation_payload = dict(validation)
    validation_declared = validation_payload.pop("content_sha256", "")
    expected_checks = {
        "content_hash", "schema_status", "old_outputs_bound",
        "implementation_bindings", "freeze_checks", "v5_output_absent",
    }
    if not (
        canonical_hash(freeze_payload) == freeze_declared
        and freeze.get("status")
        == "POST_ORACLE_CONFORMANCE_CORRECTION_FROZEN_BEFORE_SCORING_V5"
        and freeze.get("bindings", {}).get("src/score_identifiability_v5.py")
        == sha(EXP / "src/score_identifiability_v5.py")
        and freeze.get("bindings", {}).get("src/run_identifiability_scoring_v5.py")
        == sha(Path(__file__))
        and canonical_hash(validation_payload) == validation_declared
        and validation.get("schema")
        == "GDT395_SCORER_VALIDATOR_CONFORMANCE_V5_VALIDATION_V1"
        and validation.get("status") == "PASS"
        and validation.get("freeze_sha256") == sha(freeze_path)
        and validation.get("validator_sha256")
        == sha(EXP / "src/validate_scorer_validator_conformance_v5.py")
        and validation.get("checks_total") == 6
        and validation.get("checks_passed") == 6
        and set(validation.get("checks", {})) == expected_checks
        and all(type(value) is bool and value
                for value in validation.get("checks", {}).values())
    ):
        raise RuntimeError("V5 correction lineage is not frozen and PASS-bound")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir", type=Path,
        default=EXP / "artifacts/gdt395_identifiability_scores_v5",
    )
    args = parser.parse_args()
    require_correction_lineage()
    freeze_path = EXP / "artifacts/gdt395_blind_claims_freeze.json"
    validation_path = EXP / "artifacts/gdt395_blind_claims_validation.json"
    manifest_path = EXP / "artifacts/gdt395_corpus_manifest.tsv"
    with freeze_path.open("r", encoding="utf-8") as handle:
        freeze = json.load(handle)
    argv = [
        "--claims-freeze", str(freeze_path),
        "--claims-validation", str(validation_path),
        "--corpus-manifest", str(manifest_path),
        "--output-dir", str(args.output_dir),
    ]
    for role, option in (
        ("authentic_event_claims", "--claims-tsv"),
        ("pair_event_claims", "--pair-claims-tsv"),
        ("world_claims", "--world-claim-json"),
    ):
        for entry in freeze["bindings"][role]:
            argv.extend((option, str(ROOT / entry["path"])))
    with manifest_path.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if 15 <= int(row["corpus_seed"]) <= 19:
                argv.extend(("--oracle-tsv", str(EXP / ".work/corpora" / row["oracle_relpath"])))
    return scorer.main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
