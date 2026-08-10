#!/usr/bin/env python3
"""Freeze one F69M001 target and validation."""

from __future__ import annotations

import hashlib,json,subprocess
from pathlib import Path

BASE=Path(__file__).resolve().parent;ROOT=BASE.parent.parent;OUT=BASE/'F69M001_TARGET_FREEZE.json'
FILES=(
'experiments/semantic_assumptions/F69M001_LUNAR_MANSION_PREFIX_METHOD.md','experiments/semantic_assumptions/f69v_lunar_mansion_agrippa_roster.tsv',
'experiments/semantic_assumptions/audit_f69m001_capacity.py','experiments/semantic_assumptions/results/f69m001_capacity.json','experiments/semantic_assumptions/results/f69m001_capacity.md',
'experiments/semantic_assumptions/f69m001_core.py','experiments/semantic_assumptions/run_f69m001_controls.py','experiments/semantic_assumptions/results/f69m001_controls.json',
'experiments/semantic_assumptions/results/f69m001_controls.md','experiments/semantic_assumptions/validate_f69m001_controls.py',
'experiments/semantic_assumptions/results/f69m001_controls_validation.json','experiments/semantic_assumptions/results/f69m001_controls_validation.md',
'experiments/semantic_assumptions/run_f69m001_target.py','experiments/semantic_assumptions/validate_f69m001_target.py',
'experiments/semantic_assumptions/freeze_f69m001_target.py',
'experiments/semantic_assumptions/results/source_sta_family_consensus_loci.tsv','experiments/semantic_assumptions/results/source_sta_family_consensus_validation.json',
'transcription/voynich_stolfi25e1_lines.tsv')
TARGETS=tuple(f'experiments/semantic_assumptions/results/f69m001_target{x}' for x in ('.json','.md','_validation.json','_validation.md'))
def sha(path:Path)->str:return hashlib.sha256(path.read_bytes()).hexdigest()
def main()->None:
    if OUT.exists():raise SystemExit('refusing overwrite')
    if subprocess.check_output(['git','status','--porcelain'],cwd=ROOT).strip():raise SystemExit('working tree not clean')
    if any((ROOT/name).exists() for name in TARGETS):raise SystemExit('target exists')
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    result={"experiment":"F69M001_TARGET_FREEZE","status":"FROZEN_TARGET_AND_VALIDATION_ABSENT","code_commit":commit,
            "frozen_files":{name:sha(ROOT/name) for name in FILES},"target_outputs":list(TARGETS),
            "target_outputs_absent":{name:not (ROOT/name).exists() for name in TARGETS},"authorized_runs":{"target":1,"validation":1},
            "claim_ceiling":"Hash freeze only; no f69v prefix alignment, mansion identity, name, meaning, plaintext, or translation."}
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps({"status":result['status'],"files":len(FILES),"commit":commit},sort_keys=True))
if __name__=='__main__':main()
