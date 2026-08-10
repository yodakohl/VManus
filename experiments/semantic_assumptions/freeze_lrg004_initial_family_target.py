#!/usr/bin/env python3
"""Freeze the simultaneous all-24 LRG004 manuscript target."""
from __future__ import annotations
import hashlib,json,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];OUT=HERE/"LRG004_TARGET_FREEZE.json";FILES=["experiments/semantic_assumptions/LRG004_INITIAL_FAMILY_TARGET_METHOD.md","experiments/semantic_assumptions/LRG004_INITIAL_FAMILY_DISCOVERY_CALIBRATION_SPEC.md","experiments/semantic_assumptions/lrg004_core.py","experiments/semantic_assumptions/run_lrg004_initial_family_target.py","experiments/semantic_assumptions/validate_lrg004_initial_family_target.py","experiments/semantic_assumptions/freeze_lrg004_initial_family_target.py","experiments/semantic_assumptions/validate_lrg004_target_blind_calibration.py","experiments/semantic_assumptions/results/lrg001_label_register_capacity.tsv","experiments/semantic_assumptions/results/lrg004_target_blind_calibration.json","experiments/semantic_assumptions/results/lrg004_target_blind_calibration_validation.json","experiments/semantic_assumptions/results/source_sta_family_consensus_groups.tsv"];RESULTS=["experiments/semantic_assumptions/results/lrg004_initial_family_target.json","experiments/semantic_assumptions/results/lrg004_initial_family_target_report.md","experiments/semantic_assumptions/results/lrg004_initial_family_target_validation.json","experiments/semantic_assumptions/results/lrg004_initial_family_target_validation_report.md"]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    if OUT.exists() or any((ROOT/path).exists() for path in RESULTS):raise RuntimeError("target artifact exists")
    if subprocess.check_output(["git","status","--porcelain"],cwd=ROOT,text=True):raise RuntimeError("working tree dirty")
    validation=json.loads((ROOT/"experiments/semantic_assumptions/results/lrg004_target_blind_calibration_validation.json").read_text())
    if validation["status"]!="PASS_INDEPENDENT_LRG004_CALIBRATION_RECONSTRUCTION":raise RuntimeError("calibration validation absent")
    value={"status":"FROZEN_LRG004_ALL_24_TARGET","code_commit":subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),"frozen_files":{path:sha(ROOT/path) for path in FILES},"result_paths":RESULTS,"result_paths_absent":True,"claim_ceiling":"Registered families are only stable manual-label-associated group-initial codes, never prefixes classifiers morphemes words POS names identifiers sounds meanings plaintext or translation."};temporary=OUT.with_suffix(".json.tmp");temporary.write_text(json.dumps(value,indent=2,sort_keys=True)+"\n",encoding="utf-8",newline="\n");temporary.replace(OUT);print(json.dumps(value,indent=2,sort_keys=True))
if __name__=="__main__":main()
