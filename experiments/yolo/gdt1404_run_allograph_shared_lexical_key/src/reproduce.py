"""Replay the predeclared engineering gate and local shared-key screen."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys,tempfile
D=Path(__file__).resolve().parents[1];R=D.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 spec=json.loads((D/'src/SPEC.json').read_text());names=['CONTROL.json','GATE_VALIDATION.json','RESULT.json','VALIDATION.json']
 with tempfile.TemporaryDirectory(prefix='vmanus1404replay_') as tmp:
  root=Path(tmp);rel=D.relative_to(R);shutil.copytree(D,root/rel,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
  for inp in spec['inputs']:
   p=root/inp['path'];p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/inp['path'],p)
  for n in names:(root/rel/'artifacts'/n).unlink(missing_ok=True)
  commands=[['run.py','--gate'],['validate.py','--gate'],['run.py','--native'],['validate.py']]
  for c in commands:subprocess.run([sys.executable,str(root/rel/'src'/c[0]),*c[1:]],cwd=root,check=True,stdout=subprocess.DEVNULL)
  exact={n:sha(D/'artifacts'/n)==sha(root/rel/'artifacts'/n) for n in names};assert all(exact.values()),exact
  print(json.dumps({'status':'PASS','byte_exact':exact,'scope':'Replay of fixed engineering gate and local lexical constraint test; not language or meaning confirmation.'},sort_keys=True))
if __name__=='__main__':main()
