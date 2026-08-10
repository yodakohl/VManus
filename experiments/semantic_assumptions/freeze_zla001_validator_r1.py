#!/usr/bin/env python3
"""Freeze the report-order-only ZLA001 target validator replacement."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path


BASE = Path(__file__).resolve().parent
ROOT = BASE.parent.parent
R = BASE / "results"
ORIGINAL = ROOT / "ZLA001_TARGET_FREEZE.json"
AMENDMENT = ROOT / "ZLA001_TARGET_VALIDATOR_AMENDMENT.md"
VALIDATOR = BASE / "validate_zla001_target.py"
TARGET = R / "zla001_target.json"
REPORT = R / "zla001_target.md"
VALIDATION = R / "zla001_target_validation.json"
VALIDATION_REPORT = R / "zla001_target_validation.md"
OUT = ROOT / "ZLA001_TARGET_VALIDATOR_R1_FREEZE.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if OUT.exists(): raise SystemExit("refusing overwrite")
    if VALIDATION.exists() or VALIDATION_REPORT.exists(): raise AssertionError("validation output already exists")
    frozen=json.loads(ORIGINAL.read_text())
    if frozen.get("status")!="FROZEN_TARGET_AND_VALIDATION_ABSENT": raise AssertionError("original freeze")
    validator_rel="experiments/semantic_assumptions/validate_zla001_target.py"
    original_validator=frozen["files"][validator_rel]
    for relative,digest in frozen["files"].items():
        if relative==validator_rel: continue
        if sha(ROOT/relative)!=digest: raise AssertionError(f"unexpected original-file drift: {relative}")
    if not all(path.is_file() for path in (AMENDMENT,VALIDATOR,TARGET,REPORT,Path(__file__))): raise AssertionError("replacement input absent")
    commit=subprocess.run(["git","rev-parse","HEAD"],cwd=ROOT,check=True,capture_output=True,text=True).stdout.strip()
    result={
        "experiment":"ZLA001_TARGET_VALIDATOR_R1_FREEZE",
        "status":"FROZEN_REPORT_ORDER_VALIDATOR_REPLACEMENT",
        "source_commit":commit,
        "original_freeze_sha256":sha(ORIGINAL),
        "original_validator_sha256":original_validator,
        "amendment_sha256":sha(AMENDMENT),
        "replacement_validator_sha256":sha(VALIDATOR),
        "replacement_freezer_sha256":sha(Path(__file__)),
        "immutable_target_sha256":sha(TARGET),
        "immutable_report_sha256":sha(REPORT),
        "validation_absence":{str(VALIDATION.relative_to(ROOT)):True,str(VALIDATION_REPORT.relative_to(ROOT)):True},
        "allowed_change":"validator report positive_folio_counts renders explicit ZL3b IT2a RF1b order only",
        "claim_ceiling":"Validation repair only; no target rerun or change to any statistic, gate, result, meaning, plaintext, or translation.",
    }
    OUT.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print(json.dumps({"status":result["status"],"source_commit":commit,"target_sha256":result["immutable_target_sha256"],"replacement_validator_sha256":result["replacement_validator_sha256"]},sort_keys=True))


if __name__=="__main__": main()
