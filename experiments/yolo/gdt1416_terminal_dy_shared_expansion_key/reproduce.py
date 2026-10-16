#!/usr/bin/env python3
"""Isolated replay, retaining scientific STOP and UNKNOWN states."""
import argparse,hashlib,json,shutil,subprocess,sys,tempfile
from pathlib import Path
E=Path(__file__).resolve().parent;ROOT=E.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--isolated',action='store_true');p.parse_args()
    names=['CONTROL.json','GATE_VALIDATION.json']
    phases=[('run.py','--gate'),('validate.py','--gate')]
    if (E/'artifacts/RESULT.json').exists():names+=['RESULT.json','VALIDATION.json'];phases += [('run.py','--native'),('validate.py','--native')]
    expected={n:sha(E/'artifacts'/n) for n in names};lock=json.loads((E/'LOCK.json').read_text());rel=E.relative_to(ROOT)
    with tempfile.TemporaryDirectory(prefix='vmanus1416-') as d:
        target=Path(d)
        for f in [*lock['files'],str(rel/'LOCK.json')]:
            dest=target/f;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/f,dest)
        (target/rel/'artifacts').mkdir(exist_ok=True)
        for script,flag in phases:subprocess.run([sys.executable,str(rel/'src'/script),flag],cwd=target,check=True,stdout=subprocess.PIPE,text=True)
        actual={n:sha(target/rel/'artifacts'/n) for n in names}
        receipt=dict(status='PASS_BYTE_IDENTICAL_ISOLATED_REPLAY' if expected==actual else 'REPLAY_BYTES_DIFFER',expected=expected,actual=actual)
        (E/'artifacts/REPLAY.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n');print(receipt['status']);assert expected==actual
if __name__=='__main__':main()
