#!/usr/bin/env python3
"""Package manual judgments; no automated visual or semantic inference."""
from pathlib import Path
import hashlib,json
B=Path(__file__).resolve().parents[1]
R=B.parents[2]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    lock=json.loads((B/'src/PREREG_LOCK.json').read_text())
    for path,h in lock['files'].items(): assert sha(R/path)==h,path
    d=json.loads((B/'artifacts/DECISIONS.json').read_text())
    assert [c['attribute'] for c in d['cells']]==list(range(1,7))
    paths=sorted(p for p in (B/'artifacts').glob('*') if p.is_file() and p.name not in {'RESULT.json','VALIDATION.json'})
    d.update(status='COMPLETE_NATIVE_ATTRIBUTE_COMPARISON',operation='Packages manual judgments, not automated visual inference',receipts={str(p.relative_to(R)):sha(p) for p in paths})
    (B/'artifacts/RESULT.json').write_text(json.dumps(d,indent=2)+'\n')
    print(d['decision'])
if __name__=='__main__': main()
