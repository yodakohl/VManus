"""Byte-exact replay in an isolated workspace; no new data or perception."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys,tempfile
D=Path(__file__).resolve().parents[1];R=D.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 spec=json.loads((D/'src/SPEC.json').read_text());names=['SOURCE_ENVELOPES.json.gz','NATIVE_SUPPORT.json.gz','RESULT.json','VALIDATION.json']
 with tempfile.TemporaryDirectory(prefix='vmanus1403replay_') as tmp:
  root=Path(tmp);rel=D.relative_to(R);shutil.copytree(D,root/rel,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
  for inp in spec['inputs']:
   p=root/inp['path'];p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/inp['path'],p)
  for n in names:(root/rel/'artifacts'/n).unlink(missing_ok=True)
  for script in ['run.py','validate.py']:subprocess.run([sys.executable,str(root/rel/'src'/script)],cwd=root,check=True,stdout=subprocess.DEVNULL)
  exact={n:sha(D/'artifacts'/n)==sha(root/rel/'artifacts'/n) for n in names};assert all(exact.values()),exact
  print(json.dumps({'status':'PASS','byte_exact':exact,'scope':'Isolated replay of fixed source/native pattern accounting; no new manuscript or source-language confirmation.'},sort_keys=True))
if __name__=='__main__':main()
