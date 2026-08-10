#!/usr/bin/env python3
"""Freeze exact public CCT002 target files with outputs absent."""
from __future__ import annotations
import hashlib,json,os,subprocess,tempfile
from pathlib import Path
B=Path(__file__).resolve().parent;R=B/"results";OUT=B/"CCT002_TARGET_FREEZE.json";FILES=(B/"CCT002_TARGET_METHOD.md",B/"CCT002_SYNTHETIC_PREFLIGHT_SPEC.md",B/"cct002_core.py",B/"run_cct002_target.py",B/"validate_cct002_target.py",R/"cho_che_canonical_transfer_masked_panel.tsv",R/"source_separator_transcription.tsv",R/"cct002_marginal_merger_capacity_validation.json",R/"cct002_synthetic_preflight.json",R/"cct002_synthetic_preflight_validation.json");OUTPUTS=(R/"cct002_target.json",R/"cct002_target.md",R/"cct002_target_validation.json",R/"cct002_target_validation.md")
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 if OUT.exists() or any(p.exists() for p in OUTPUTS):raise SystemExit("output exists")
 if subprocess.check_output(["git","status","--porcelain"],cwd=B,text=True).strip():raise SystemExit("dirty")
 commit=subprocess.check_output(["git","rev-parse","HEAD"],cwd=B,text=True).strip();files={p.name:sha(p) for p in FILES};absence={p.name:not p.exists() for p in OUTPUTS};result={"experiment":"CCT002_TARGET_FREEZE","status":"FROZEN_CCT002_TARGET_AND_VALIDATION_ABSENT","code_commit":commit,"files":files,"required_files":sorted(files),"output_absence":absence,"claim_ceiling":"Freeze only; no target result meaning or translation."}
 with tempfile.TemporaryDirectory(prefix="cct002f_",dir=B) as d:
  q=Path(d)/"f";q.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");os.link(q,OUT)
 print(json.dumps({"status":result["status"],"commit":commit,"files":len(files),"outputs_absent":all(absence.values())},sort_keys=True))
if __name__=="__main__":main()
