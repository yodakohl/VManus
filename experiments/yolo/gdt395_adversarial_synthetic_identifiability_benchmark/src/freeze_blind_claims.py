#!/usr/bin/env python3
"""Freeze GDT395 decoder claims before any sealed truth is opened."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
EXP = ROOT / "experiments/yolo/gdt395_adversarial_synthetic_identifiability_benchmark"
CLAIMS = EXP / ".work/claims"
MANIFEST = CLAIMS / "blind_claim_manifest_all.tsv"
OUT = EXP / "artifacts/gdt395_blind_claims_freeze.json"
DECODER_FREEZE = EXP / "artifacts/gdt395_decoder_panel_freeze.json"
RECOVERY_VALIDATION = EXP / "artifacts/gdt395_v3_interruption_recovery_validation.json"


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def repo_path(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT.resolve()))


def valid_content(data: dict) -> bool:
    copy = dict(data)
    expected = copy.pop("content_sha256", "")
    raw = json.dumps(copy, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(raw).hexdigest() == expected


def main() -> None:
    if OUT.exists():
        raise RuntimeError(f"refusing to overwrite one-shot claims freeze: {OUT}")
    with MANIFEST.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh, delimiter="\t"))
    if len(rows) != 2150:
        raise RuntimeError(f"expected 2150 claim files, got {len(rows)}")
    for row in rows:
        path = CLAIMS / row["claim_relpath"]
        if not path.is_file() or sha(path) != row["claim_sha256"]:
            raise RuntimeError(f"claim hash mismatch: {path}")
    claim_bindings = {
        "authentic_event_claims": [],
        "pair_event_claims": [],
        "world_claims": [],
    }
    for row in rows:
        path = CLAIMS / row["claim_relpath"]
        binding = {"path": repo_path(path), "sha256": row["claim_sha256"]}
        if row["mode"] == "world_claim":
            claim_bindings["world_claims"].append(binding)
        elif row["mode"] == "pair":
            claim_bindings["pair_event_claims"].append(binding)
        else:
            claim_bindings["authentic_event_claims"].append(binding)
    implementation = {}
    for rel in (
        "artifacts/gdt395_decoder_panel_freeze.json",
        "artifacts/gdt395_decoder_panel_validation.json",
        "artifacts/gdt395_decoder_execution_correction.json",
        "artifacts/gdt395_decoder_execution_correction_validation.json",
        "artifacts/gdt395_corpus_manifest.tsv",
        "artifacts/gdt395_pair_blind_manifest.tsv",
        "src/decoder_api.py",
        "src/run_blind_decoders.py",
        "src/run_blind_decoders_v2.py",
        "src/run_blind_decoders_v3.py",
        "artifacts/gdt395_decoder_execution_v3_correction.json",
        "artifacts/gdt395_decoder_execution_v3_correction_validation.json",
        "artifacts/gdt395_runner_cache_equivalence_validation.json",
        "SCORING_DESIGN.md",
        "SCORING_REVIEW.md",
        "VALIDATION_DESIGN.md",
        "VALIDATION_REVIEW.md",
        "INTERRUPTION_RECOVERY.md",
        "artifacts/gdt395_v3_interruption_recovery_freeze.json",
        "artifacts/gdt395_v3_interruption_recovery_result.json",
        "artifacts/gdt395_v3_interruption_recovery_validation.json",
        "src/freeze_blind_claims.py",
        "src/score_identifiability.py",
        "src/validate_blind_claims.py",
        "src/validate_identifiability.py",
        "src/freeze_v3_interrupted_recovery.py",
        "src/recover_v3_interrupted_completion.py",
        "src/validate_v3_interrupted_completion.py",
    ):
        implementation[rel] = sha(EXP / rel)
    decoder_freeze = json.loads(DECODER_FREEZE.read_text())
    recovery_validation = json.loads(RECOVERY_VALIDATION.read_text())
    implementation_map = {}
    for row in decoder_freeze["decoders"]:
        meta = row["meta"]
        designer = meta["designer_model"].lower()
        model_family = "LUNA" if "luna" in designer else "SOL" if "sol" in designer else ""
        implementation_map[meta["decoder_id"]] = {
            "decoder_id": meta["decoder_id"],
            "model_family": model_family,
            "oracle_blind": meta["oracle_blind"],
            "source_sha256": row["source_sha256"],
        }
    mode_counts = {
        "authentic_event_claims": sum(r["mode"] == "authentic" for r in rows),
        "pair_event_claims": sum(r["mode"] == "pair" for r in rows),
        "world_claims": sum(r["mode"] == "world_claim" for r in rows),
    }
    checks = {
        "claim_file_count_2150": len(rows) == 2150,
        "authentic_claim_count_1500": mode_counts["authentic_event_claims"] == 1500,
        "pair_claim_count_600": mode_counts["pair_event_claims"] == 600,
        "world_claim_count_50": mode_counts["world_claims"] == 50,
        "two_sol_three_luna": (
            sum(v["model_family"] == "SOL" for v in implementation_map.values()) == 2
            and sum(v["model_family"] == "LUNA" for v in implementation_map.values()) == 3
        ),
        "all_decoders_oracle_blind": all(v["oracle_blind"] is True for v in implementation_map.values()),
        "all_claim_hashes_verified": True,
        "interruption_recovery_validated": (
            valid_content(recovery_validation)
            and recovery_validation.get("schema") == "GDT395_V3_INTERRUPTION_RECOVERY_VALIDATION_V1"
            and recovery_validation.get("status") == "PASS"
            and recovery_validation.get("checks_total") == recovery_validation.get("checks_passed")
            and bool(recovery_validation.get("checks"))
            and all(type(value) is bool and value
                    for value in recovery_validation.get("checks", {}).values())
        ),
        "oracle_unopened": True,
        "voynich_and_f84_absent": True,
    }
    if not all(checks.values()):
        failed = ",".join(name for name, passed in checks.items() if not passed)
        raise RuntimeError(f"claims freeze checks failed: {failed}")
    data = {
        "schema": "GDT395_BLIND_CLAIMS_FREEZE_V2",
        "status": "PASS",
        "phase": "FROZEN_BEFORE_ORACLE_ACCESS",
        "claim_file_count": len(rows),
        "event_claim_file_count": sum(r["mode"] != "world_claim" for r in rows),
        "world_claim_file_count": sum(r["mode"] == "world_claim" for r in rows),
        "claim_manifest": {"path": repo_path(MANIFEST), "sha256": sha(MANIFEST)},
        "bindings": {**claim_bindings, "implementation": {"hashes": implementation}},
        "implementation_map": implementation_map,
        "checks": checks,
        "oracle_blind": True,
        "oracle_opened": False,
        "oracle_rows_read": 0,
        "voynich_rows": 0,
        "f84": {"opened": False, "parsed": False, "retained": False, "scored": False},
    }
    raw = json.dumps(data, sort_keys=True, separators=(",", ":")).encode()
    data["content_sha256"] = hashlib.sha256(raw).hexdigest()
    OUT.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": data["status"], "claim_files": len(rows)}, sort_keys=True))


if __name__ == "__main__":
    main()
