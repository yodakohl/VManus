#!/usr/bin/env python3
"""Freeze the one-shot aggregate LRG002 manuscript target."""

from __future__ import annotations
import hashlib,json,subprocess
from pathlib import Path

HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[1]; OUT=HERE/"LRG002_TARGET_FREEZE.json"
FILES=[
"experiments/semantic_assumptions/LRG002_PROSE_SLOT_TARGET_METHOD.md","experiments/semantic_assumptions/LRG002_TARGET_BLIND_SLOT_CALIBRATION_SPEC.md","experiments/semantic_assumptions/LRG002_PROSE_SLOT_PROJECTION_CAPACITY_SPEC.md",
"experiments/semantic_assumptions/lrg001_core.py","experiments/semantic_assumptions/lrg002_core.py","experiments/semantic_assumptions/run_lrg002_prose_slot_target.py","experiments/semantic_assumptions/validate_lrg002_prose_slot_target.py","experiments/semantic_assumptions/freeze_lrg002_prose_slot_target.py",
"experiments/semantic_assumptions/validate_lrg001_target_blind_calibration_v2.py","experiments/semantic_assumptions/validate_lrg002_target_blind_calibration.py",
"experiments/semantic_assumptions/results/lrg001_label_register_capacity.tsv","experiments/semantic_assumptions/results/lrg001_label_register_target_recovered.json","experiments/semantic_assumptions/results/lrg001_label_register_target_recovered_validation.json",
"experiments/semantic_assumptions/results/lrg002_prose_slot_capacity.tsv","experiments/semantic_assumptions/results/lrg002_prose_slot_capacity_validation.json","experiments/semantic_assumptions/results/lrg002_target_blind_calibration.json","experiments/semantic_assumptions/results/lrg002_target_blind_calibration_validation.json","experiments/semantic_assumptions/results/source_sta_family_consensus_groups.tsv"]
RESULTS=["experiments/semantic_assumptions/results/lrg002_prose_slot_target.json","experiments/semantic_assumptions/results/lrg002_prose_slot_target_report.md","experiments/semantic_assumptions/results/lrg002_prose_slot_target_validation.json","experiments/semantic_assumptions/results/lrg002_prose_slot_target_validation_report.md"]
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    if OUT.exists() or any((ROOT/path).exists() for path in RESULTS): raise RuntimeError("target artifact exists")
    if subprocess.check_output(["git","status","--porcelain"],cwd=ROOT,text=True): raise RuntimeError("working tree dirty")
    calibration=json.loads((ROOT/"experiments/semantic_assumptions/results/lrg002_target_blind_calibration_validation.json").read_text())
    if calibration["status"]!="PASS_INDEPENDENT_LRG002_CALIBRATION_RECONSTRUCTION": raise RuntimeError("calibration validation absent")
    value={"status":"FROZEN_LRG002_SINGLE_TARGET","code_commit":subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),"frozen_files":{path:sha(ROOT/path) for path in FILES},"result_paths":RESULTS,"result_paths_absent":True,"claim_ceiling":"One target may establish only a distributed corrected-segment position of relative label-profile likeness, never a word name identifier noun POS meaning plaintext or translation."}
    temporary=OUT.with_suffix(".json.tmp"); temporary.write_text(json.dumps(value,indent=2,sort_keys=True)+"\n",encoding="utf-8",newline="\n"); temporary.replace(OUT); print(json.dumps(value,indent=2,sort_keys=True))
if __name__=="__main__": main()
