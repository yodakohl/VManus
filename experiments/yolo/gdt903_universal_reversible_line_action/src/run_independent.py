#!/usr/bin/env python3
"""Enforce the registered600-second independent construction/folding budget."""
import hashlib,json,subprocess,sys,time
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
def main():
    started=time.monotonic();receipt={'budget_seconds':600}
    try:
        p=subprocess.run([sys.executable,str(BASE/'src/independent_subgroup.py'),'--source',str(BASE/'artifacts/SOURCE_LINES.json'),'--reference','f19r.8','--output',str(BASE/'artifacts/INDEPENDENT_SUBGROUP.json')],capture_output=True,text=True,timeout=600)
        receipt.update(exit_code=p.returncode,stdout=p.stdout,stderr_sha256=hashlib.sha256(p.stderr.encode()).hexdigest(),stderr_empty=not p.stderr)
    except subprocess.TimeoutExpired:receipt['status']='UNKNOWN_BUDGET'
    receipt['elapsed_seconds']=time.monotonic()-started
    (BASE/'artifacts/INDEPENDENT_RUN_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
