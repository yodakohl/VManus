#!/usr/bin/env python3
"""Exact staged-input isolated replay; never changes the original artifacts."""
import argparse,hashlib,json,shutil,subprocess,sys,tempfile
from pathlib import Path
E=Path(__file__).resolve().parent;ROOT=E.parents[2]
NAMES=['CONTROL.json','GATE_VALIDATION.json','RESULT.json','VALIDATION.json']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--isolated',action='store_true');args=parser.parse_args()
    lock=json.loads((E/'LOCK.json').read_text());rel=E.relative_to(ROOT)
    expected={n:sha(E/'artifacts'/n) for n in NAMES}
    with tempfile.TemporaryDirectory(prefix='vmanus1414-') as d:
        target=Path(d)
        for f in [*lock['files'],str(rel/'LOCK.json')]:
            dest=target/f;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/f,dest)
        (target/rel/'artifacts').mkdir(exist_ok=True)
        for script,flag in [('run.py','--gate'),('validate.py','--gate'),('run.py','--native'),('validate.py','--native')]:
            subprocess.run([sys.executable,str(rel/'src'/script),flag],cwd=target,check=True,stdout=subprocess.PIPE,text=True)
        actual={n:sha(target/rel/'artifacts'/n) for n in NAMES}
        receipt=dict(status='PASS_BYTE_IDENTICAL_ISOLATED_REPLAY' if actual==expected else 'REPLAY_BYTES_DIFFER',expected=expected,actual=actual,isolated=True)
        (E/'artifacts/REPLAY.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
        print(receipt['status']);assert actual==expected
if __name__=='__main__':main()
