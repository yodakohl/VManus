#!/usr/bin/env python3
"""Create the public no-target CCT001 hash freeze once."""
from __future__ import annotations
import hashlib,json,os,subprocess,tempfile
from pathlib import Path
B=Path(__file__).resolve().parent;R=B/"results";OUT=B/"CCT001_TARGET_FREEZE.json"
FILES=(B/"CHO_CHE_CANONICAL_TRANSFER_TARGET_METHOD.md",B/"CHO_CHE_CANONICAL_TRANSFER_SYNTHETIC_PREFLIGHT_SPEC.md",B/"cho_che_canonical_transfer_core.py",B/"run_cho_che_canonical_transfer_target.py",B/"validate_cho_che_canonical_transfer_target.py",R/"cho_che_canonical_transfer_masked_panel.tsv",R/"source_separator_transcription.tsv",R/"cho_che_canonical_transfer_capacity_validation.json",R/"cho_che_canonical_transfer_synthetic_preflight.json",R/"cho_che_canonical_transfer_synthetic_preflight_validation.json")
OUTPUTS=(R/"cho_che_canonical_transfer_target.json",R/"cho_che_canonical_transfer_target.md",R/"cho_che_canonical_transfer_target_validation.json",R/"cho_che_canonical_transfer_target_validation.md")
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 if OUT.exists() or any(p.exists() for p in OUTPUTS):raise SystemExit("freeze/target output exists")
 commit=subprocess.check_output(["git","rev-parse","HEAD"],cwd=B,text=True).strip()
 if subprocess.check_output(["git","status","--porcelain"],cwd=B,text=True).strip():raise SystemExit("dirty worktree")
 files={p.name:sha(p) for p in FILES}; absence={p.name:not p.exists() for p in OUTPUTS}; result={"experiment":"CCT001_TARGET_FREEZE","status":"FROZEN_CCT001_TARGET_AND_VALIDATION_ABSENT","code_commit":commit,"files":files,"required_files":sorted(files),"output_absence":absence,"claim_ceiling":"Freeze only; no target result meaning plaintext or translation."}
 with tempfile.TemporaryDirectory(prefix="cct001f_",dir=B) as d:
  q=Path(d)/"freeze";q.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");os.link(q,OUT)
 print(json.dumps({"status":result["status"],"commit":commit,"files":len(files),"outputs_absent":all(absence.values())},sort_keys=True))
if __name__=="__main__":main()
