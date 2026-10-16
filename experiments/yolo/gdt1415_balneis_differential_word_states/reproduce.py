#!/usr/bin/env python3
"""Isolated replay of hash-bound known-source inputs, no original writes."""
import argparse,hashlib,json,shutil,subprocess,sys,tempfile
from pathlib import Path
E=Path(__file__).resolve().parent;ROOT=E.parents[2]
NAMES=['CONTROLS.json','RESULT.json','VALIDATION.json']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--isolated',action='store_true');p.parse_args()
    lock=json.loads((E/'LOCK.json').read_text());rel=E.relative_to(ROOT)
    expected={n:sha(E/'artifacts'/n) for n in NAMES}
    with tempfile.TemporaryDirectory(prefix='vmanus1415-') as d:
        target=Path(d)
        for f in [*lock['files'],str(rel/'LOCK.json')]:
            dest=target/f;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/f,dest)
        (target/rel/'artifacts').mkdir(exist_ok=True)
        for script,args in [('run.py',[]),('validate.py',['--validate'])]:
            subprocess.run([sys.executable,str(rel/'src'/script),*args],cwd=target,check=True,stdout=subprocess.PIPE,text=True)
        actual={n:sha(target/rel/'artifacts'/n) for n in NAMES}
        assert actual==expected
    receipt=dict(status='PASS_BYTE_IDENTICAL_ISOLATED_REPLAY',artifacts=expected)
    (E/'artifacts/REPLAY.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n');print(receipt['status'])
if __name__=='__main__':main()
