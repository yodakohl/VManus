"""Deterministic isolated replay of a necessary-condition witness packet."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys,tempfile
D=Path(__file__).resolve().parents[1];R=D.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 s=json.loads((D/'src/SPEC.json').read_text());names=['SOURCE_CUBES.json','RESULT.json','VALIDATION.json']
 with tempfile.TemporaryDirectory(prefix='vmanus1406replay_') as tmp:
  root=Path(tmp);rel=D.relative_to(R);shutil.copytree(D,root/rel,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
  for x in s['inputs']:
   p=root/x['path'];p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/x['path'],p)
  for n in names:(root/rel/'artifacts'/n).unlink(missing_ok=True)
  for f in ['run.py','validate.py']:subprocess.run([sys.executable,str(root/rel/'src'/f)],cwd=root,check=True,stdout=subprocess.DEVNULL)
  exact={n:sha(D/'artifacts'/n)==sha(root/rel/'artifacts'/n) for n in names};assert all(exact.values()),exact
  print(json.dumps({'status':'PASS','byte_exact':exact,'scope':'Witness/sourcecube counting only; no native key, source meaning or language identified.'},sort_keys=True))
if __name__=='__main__':main()
