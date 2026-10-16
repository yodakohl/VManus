#!/usr/bin/env python3
"""Replay frozen commands; optional isolated copy of exact public inputs."""
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
E=Path(__file__).resolve().parent
ROOT=E.parents[2]
NAMES=['CONTROLS.json','PASSAGE.json','FRAMES.json','RESULT.json','VALIDATION.json']
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(root):
    rel=E.relative_to(ROOT)
    for name in ['run.py','validate.py']:
        subprocess.run([sys.executable,str(rel/'src'/name)],cwd=root,check=True,stdout=subprocess.PIPE,text=True)
def main():
    p=argparse.ArgumentParser();p.add_argument('--isolated',action='store_true');a=p.parse_args()
    expected={n:digest(E/'artifacts'/n) for n in NAMES}
    if a.isolated:
        lock=json.loads((E/'LOCK.json').read_text())
        with tempfile.TemporaryDirectory(prefix='vmanus1413-') as d:
            target=Path(d)
            for f in [*lock['files'],str((E/'LOCK.json').relative_to(ROOT))]:
                dest=target/f;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/f,dest)
            (target/E.relative_to(ROOT)/'artifacts').mkdir(exist_ok=True)
            run(target)
            actual={n:digest(target/E.relative_to(ROOT)/'artifacts'/n) for n in NAMES}
            assert actual==expected
    else:
        run(ROOT)
        assert {n:digest(E/'artifacts'/n) for n in NAMES}==expected
    receipt=dict(status='PASS_BYTE_IDENTICAL_REPLAY',isolated=a.isolated,artifacts=expected)
    (E/'artifacts'/('ISOLATED_REPLAY.json' if a.isolated else 'REPLAY.json')).write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
    print(receipt['status'])
if __name__=='__main__':main()
