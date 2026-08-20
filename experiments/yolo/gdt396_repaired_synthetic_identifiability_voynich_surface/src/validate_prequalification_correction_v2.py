#!/usr/bin/env python3
"""Validate the final GDT396 prequalification correction layer."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


def find_repo_root(start:Path)->Path:
    for candidate in (start,*start.parents):
        if (candidate/"AGENTS.md").is_file() and (candidate/".git").exists():return candidate
    raise RuntimeError("repository root not found")


ROOT=find_repo_root(Path(__file__).resolve());EXP=ROOT/"experiments/yolo/gdt396_repaired_synthetic_identifiability_voynich_surface";FREEZE=EXP/"artifacts/gdt396_prequalification_correction_freeze_v2.json";OUT=EXP/"artifacts/gdt396_prequalification_correction_validation_v2.json"


def sha256(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda:fh.read(1<<20),b""):h.update(block)
    return h.hexdigest()


def content_hash(value:dict)->str:
    clean=dict(value);clean.pop("content_sha256",None)
    return hashlib.sha256(json.dumps(clean,sort_keys=True,separators=(",",":")).encode()).hexdigest()


def main()->int:
    data=json.loads(FREEZE.read_text());v1_path=EXP/"artifacts/gdt396_prequalification_correction_freeze.json";v1=json.loads(v1_path.read_text())
    drift={rel for rel,digest in v1["bindings"].items() if sha256(EXP/rel)!=digest}
    checks={
        "schema_status":data.get("schema")=="GDT396_PREQUALIFICATION_CORRECTION_FREEZE_V2" and data.get("status")=="FROZEN_BEFORE_QUALIFICATION_GENERATION",
        "content_hash":data.get("content_sha256")==content_hash(data),"v1_bound":data.get("v1_freeze_sha256")==sha256(v1_path),
        "v1_bound_bytes_unchanged":not drift and not data.get("v1_postfreeze_drift"),
        "v1_drift_hashes":all(row.get("v1_sha256")==v1["bindings"].get(row.get("relpath")) and row.get("v2_sha256")==sha256(EXP/row["relpath"]) for row in data.get("v1_postfreeze_drift",[])),
        "bindings_exact":all((EXP/rel).is_file() and sha256(EXP/rel)==digest for rel,digest in data.get("bindings",{}).items()),
        "future_blocks_absent":not any((EXP/f".work/corpora/gdt396_{block}_paired_manifest_v2.tsv").exists() for block in ("qualification","confirmation")),
        "seals":data.get("voynich_rows")==0 and data.get("f84",{}).get("opened") is False and data.get("f84r",{}).get("opened") is False,
    }
    result={"schema":"GDT396_PREQUALIFICATION_CORRECTION_VALIDATION_V2","status":"PASS" if all(checks.values()) else "FAIL","checks":checks,"checks_passed":sum(checks.values()),"checks_total":len(checks),"freeze_sha256":sha256(FREEZE),"validator_sha256":sha256(Path(__file__)),"voynich_rows":0,"f84":{"opened":False,"rows":0},"f84r":{"opened":False,"rows":0}}
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps(result,indent=2,sort_keys=True));return 0 if result["status"]=="PASS" else 1


if __name__=="__main__":raise SystemExit(main())
