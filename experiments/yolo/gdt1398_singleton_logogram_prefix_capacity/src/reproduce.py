"""Replay locked inputs in a fresh isolated repository outside the checkout."""
from pathlib import Path
import argparse, hashlib, json, shutil, subprocess, sys, tempfile
D=Path(__file__).resolve().parents[1]
ROOT=D.parents[2]
REL=D.relative_to(ROOT)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--destination');a=ap.parse_args()
    base=Path(a.destination) if a.destination else Path(tempfile.mkdtemp(prefix='vmanus1398-'))/'repository'
    assert not base.exists() or not any(base.iterdir()),'fresh replay directory required'
    base.mkdir(parents=True,exist_ok=True)
    lock=json.loads((D/'LOCK.json').read_text())
    for p,h in lock['files'].items():
        source=ROOT/p;assert hashlib.sha256(source.read_bytes()).hexdigest()==h,p
        dest=base/p;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,dest)
    shutil.copyfile(D/'LOCK.json',base/REL/'LOCK.json')
    for name in ['run.py','validate.py']:
        subprocess.run([sys.executable,str(base/REL/'src'/name)],cwd=base,check=True,stdout=subprocess.DEVNULL)
    expected=['RESULT.json','VALIDATION.json']+[p.name for p in sorted((D/'artifacts').glob('CERTIFICATE_*.json.gz'))]
    checks={}
    for name in expected:
        actual=base/REL/'artifacts'/name;reference=D/'artifacts'/name
        checks[name]=hashlib.sha256(actual.read_bytes()).hexdigest()==hashlib.sha256(reference.read_bytes()).hexdigest()
    assert all(checks.values()),checks
    print(json.dumps({'status':'PASS','byte_exact_artifacts':checks},indent=2,sort_keys=True))
if __name__=='__main__':main()
