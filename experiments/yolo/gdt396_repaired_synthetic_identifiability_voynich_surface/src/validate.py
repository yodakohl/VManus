#!/usr/bin/env python3
"""Public GDT396 validation entry point."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists(): return candidate
    raise RuntimeError("repository root not found")


ROOT=find_repo_root(Path(__file__).resolve());EXP=ROOT/"experiments/yolo/gdt396_repaired_synthetic_identifiability_voynich_surface";SRC=EXP/"src"


def call(name:str,*args:str)->None:
    subprocess.run([sys.executable,str(SRC/name),*args],cwd=ROOT,check=True)


def main()->int:
    ap=argparse.ArgumentParser();ap.add_argument("--stage",choices=("auto","pre-panel","panel","qualification","confirmation"),default="auto");args=ap.parse_args();stage=args.stage
    correction_v3=EXP/"artifacts/gdt396_prequalification_correction_freeze_v3.json"
    correction_v2=EXP/"artifacts/gdt396_prequalification_correction_freeze_v2.json"
    correction_v1=EXP/"artifacts/gdt396_prequalification_correction_freeze.json"
    if correction_v3.exists():
        call("validate_prequalification_correction_v3.py")
    elif correction_v2.exists():
        call("validate_prequalification_correction_v2.py")
    elif correction_v1.exists():
        call("validate_prequalification_correction.py")
    else:
        call("validate_protocol.py");call("validate_paired_corpora.py")
    if stage=="auto":
        if (EXP/"artifacts/gdt396_confirmation_claim_freeze.json").exists():stage="confirmation"
        elif (EXP/"artifacts/gdt396_decoder_qualification.json").exists():stage="qualification"
        elif (EXP/"artifacts/gdt396_decoder_panel_freeze.json").exists():stage="panel"
        else:stage="pre-panel"
    if stage in {"panel","qualification","confirmation"}:call("validate_decoder_panel.py")
    if stage in {"qualification","confirmation"}:
        call("validate_phase_corpora.py","--phase","qualification")
        freeze=json.loads((EXP/"artifacts/gdt396_qualification_claim_freeze.json").read_text())
        result=json.loads((EXP/"artifacts/gdt396_decoder_qualification.json").read_text())
        if freeze.get("status")!="FROZEN_BEFORE_ORACLE_SCORING" or result.get("schema")!="GDT396_DECODER_QUALIFICATION_V1":raise RuntimeError("qualification artifacts invalid")
    if stage=="confirmation":
        call("validate_phase_corpora.py","--phase","confirmation")
        if json.loads((EXP/"artifacts/gdt396_confirmation_claim_freeze.json").read_text()).get("status")!="FROZEN_BEFORE_ORACLE_SCORING":raise RuntimeError("confirmation claims invalid")
    print(json.dumps({"schema":"GDT396_PUBLIC_VALIDATION_ENTRY_V1","stage":stage,"status":"PASS","voynich_rows":0,"f84":False,"f84r":False},sort_keys=True));return 0


if __name__=="__main__":raise SystemExit(main())
