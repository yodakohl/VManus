#!/usr/bin/env python3
"""Postresult packaging: isolate and replay the ordinary-subset certificate."""
import hashlib,json,shutil,subprocess,sys,tempfile
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    lock=json.loads((E/'DIAGNOSTIC_LOCK.json').read_text());rel=E.relative_to(ROOT)
    expected=sha(E/'artifacts/RELAXATION.json')
    with tempfile.TemporaryDirectory(prefix='vmanus1416-subset-') as d:
        target=Path(d)
        for f in [*lock['files'],str(rel/'DIAGNOSTIC_LOCK.json')]:
            dest=target/f;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/f,dest)
        subprocess.run([sys.executable,'-B',str(rel/'src/relaxation.py')],cwd=target,check=True,stdout=subprocess.PIPE,text=True)
        actual=sha(target/rel/'artifacts/RELAXATION.json');assert actual==expected
    receipt=dict(status='PASS_BYTE_IDENTICAL_RELAXATION_REPLAY',artifact_sha256=expected,diagnostic_lock_sha256=sha(E/'DIAGNOSTIC_LOCK.json'),replayer_sha256=sha(Path(__file__)),scope='Postresult subset certificate only; original14file scientificlock/code/results unchanged.')
    (E/'artifacts/RELAXATION_REPLAY.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n');print(receipt['status'])
if __name__=='__main__':main()
