#!/usr/bin/env python3
"""Independent binding validator for the pre-qualification GDT396 panel."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("repository root not found")


ROOT=find_repo_root(Path(__file__).resolve())
EXP=ROOT/"experiments/yolo/gdt396_repaired_synthetic_identifiability_voynich_surface"
FREEZE=EXP/"artifacts/gdt396_decoder_panel_freeze.json"
OUT=EXP/"artifacts/gdt396_decoder_panel_validation.json"


def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda:fh.read(1<<20),b""):h.update(block)
    return h.hexdigest()


def main()->int:
    data=json.loads(FREEZE.read_text(encoding="utf-8"));checks={}
    payload=dict(data);expected=payload.pop("content_sha256")
    checks["schema_status"]=data.get("schema")=="GDT396_DECODER_PANEL_FREEZE_V1" and data.get("status")=="FROZEN_BEFORE_QUALIFICATION_GENERATION"
    checks["content_hash"]=hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()==expected
    checks["bindings_exact"]=all((EXP/rel).is_file() and sha256(EXP/rel)==digest for rel,digest in data.get("bindings",{}).items())
    checks["decoder_bindings_exact"]=all(
        sha256(EXP/row["decoder_relpath"])==row["decoder_sha256"] and sha256(EXP/row["attestation_relpath"])==row["attestation_sha256"]
        for row in data.get("decoders",[])
    )
    checks["four_independent_methods"]=len(data.get("decoders",[]))>=4 and len({row["method_family"] for row in data.get("decoders",[])})>=4 and len({row["decoder_id"] for row in data.get("decoders",[])})==len(data.get("decoders",[]))
    review=(EXP/"DECODER_PANEL_REVIEW.md").read_text(encoding="utf-8")
    checks["independent_review_go"]="Final decision: **GO**" in review
    checks["qualification_absent_at_freeze"]=not any((EXP/".work/corpora").glob("gdt396_qualification_paired_manifest*.tsv")) and not (EXP/".work/claims/gdt396_qualification_claim_manifest.tsv").exists()
    checks["confirmation_absent_at_freeze"]=not any((EXP/".work/corpora").glob("gdt396_confirmation_paired_manifest*.tsv")) and not (EXP/".work/claims/gdt396_confirmation_claim_manifest.tsv").exists()
    correction=json.loads((EXP/"artifacts/gdt396_prequalification_correction_validation_v3.json").read_text())
    checks["versioned_prequalification_correction_pass"]=correction.get("status")=="PASS"
    historical_protocol=json.loads((EXP/"artifacts/gdt396_protocol_validation.json").read_text())
    historical_corpus=json.loads((EXP/"artifacts/gdt396_development_corpus_validation.json").read_text())
    checks["historical_failures_narrow"]=([k for k,v in historical_protocol["checks"].items() if not v]==["protocol_hashes"] and [k for k,v in historical_corpus["checks"].items() if not v]==["protocol_valid"])
    checks["f84_sealed"]=data.get("f84",{}).get("opened") is False and data.get("f84r",{}).get("opened") is False and data.get("voynich_rows")==0
    result={"schema":"GDT396_DECODER_PANEL_VALIDATION_V1","status":"PASS" if all(checks.values()) else "FAIL","checks":checks,"checks_passed":sum(checks.values()),"checks_total":len(checks),"freeze_sha256":sha256(FREEZE),"validator_sha256":sha256(Path(__file__)),"f84":{"opened":False,"rows":0},"f84r":{"opened":False,"rows":0}}
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True));return 0 if result["status"]=="PASS" else 1


if __name__=="__main__":raise SystemExit(main())
