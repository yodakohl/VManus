#!/usr/bin/env python3
"""Seal the post-HOLD GDT396 prequalification enforcement corrections."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists(): return candidate
    raise RuntimeError("repository root not found")


ROOT=find_repo_root(Path(__file__).resolve());EXP=ROOT/"experiments/yolo/gdt396_repaired_synthetic_identifiability_voynich_surface";OUT=EXP/"artifacts/gdt396_prequalification_correction_freeze_v2.json"


def sha256(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda:fh.read(1<<20),b""):h.update(block)
    return h.hexdigest()


def content_hash(value:dict)->str:
    clean=dict(value);clean.pop("content_sha256",None)
    return hashlib.sha256(json.dumps(clean,sort_keys=True,separators=(",",":")).encode()).hexdigest()


def main()->int:
    if OUT.exists():raise RuntimeError(f"refusing to overwrite {OUT}")
    if any((EXP/f".work/corpora/gdt396_{block}_paired_manifest_v2.tsv").exists() for block in ("qualification","confirmation")):raise RuntimeError("future observations already exist")
    v1_path=EXP/"artifacts/gdt396_prequalification_correction_freeze.json";v1=json.loads(v1_path.read_text())
    drift=[{"relpath":rel,"v1_sha256":digest,"v2_sha256":sha256(EXP/rel)} for rel,digest in v1["bindings"].items() if sha256(EXP/rel)!=digest]
    if drift:raise RuntimeError(f"unexpected drift in V1-bound bytes: {drift}")
    fixed=(
        "PREQUALIFICATION_REAUDIT_CORRECTION.md","src/phase_authority.py","src/generate_paired_corpora.py",
        "src/run_blind_decoders.py","src/score_decoder_phase.py","src/qualify_decoders.py","src/freeze_claims.py",
        "src/validate_phase_corpora.py","src/test_instrument_contract.py","src/freeze_decoder_panel.py",
        "src/validate_decoder_panel.py","src/freeze_prequalification_correction_v2.py","src/validate_prequalification_correction_v2.py",
        "src/run.py","src/validate.py",
        "artifacts/gdt396_protocol_freeze.json","artifacts/gdt396_protocol_validation.json",
        "artifacts/gdt396_development_corpus_validation.json","artifacts/gdt396_prequalification_correction_freeze.json",
        "artifacts/gdt396_prequalification_correction_validation.json",
        ".work/corpora/gdt396_legacy_paired_manifest_v2.tsv",".work/corpora/gdt396_development_paired_manifest_v2.tsv",
    )
    result={
        "schema":"GDT396_PREQUALIFICATION_CORRECTION_FREEZE_V2","status":"FROZEN_BEFORE_QUALIFICATION_GENERATION",
        "v1_freeze_sha256":sha256(v1_path),"v1_postfreeze_drift":drift,
        "v2_reasons":{
            "expanded_binding_surface":"bind the post-review runner, scorer, qualifier, claim freezer, action-time authority, public entry points, panel freezer/validator, and adversarial fixtures omitted from correction V1",
            "logical_claim_integrity":"enforce logical-key uniqueness, status-dependent emptiness, and morphology rank limits before scoring",
            "action_time_authority":"authenticate current instrument and blind-claim freezes instead of trusting stored PASS literals",
            "semantics_light_guard":"require explicit event-level W10 false-positive rates for scored and no-capacity rows",
        },
        "qualification_observations_generated":False,"confirmation_observations_generated":False,
        "bindings":{rel:sha256(EXP/rel) for rel in fixed},
        "voynich_corpus_files_opened":0,"voynich_rows":0,
        "f84":{"allowed":False,"opened":False,"rows":0},"f84r":{"allowed":False,"opened":False,"rows":0},
    }
    result["content_sha256"]=content_hash(result);OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(OUT,sha256(OUT),result["content_sha256"]);return 0


if __name__=="__main__":raise SystemExit(main())
