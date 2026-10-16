"""Fixed-source isolated replay; old files remain byte-frozen."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys,tempfile
D=Path(__file__).resolve().parents[1];R=D.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 s=json.loads((D/'src/SPEC.json').read_text());names=['FAMILIES.json.gz','RESULT.json','VALIDATION.json']+['CERT_'+e+'_'+p+'.json.gz' for e in s['readers'] for p in s['panels']]
 with tempfile.TemporaryDirectory(prefix='vmanus1405replay_') as temp:
  root=Path(temp);rel=D.relative_to(R);shutil.copytree(D,root/rel,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
  for x in s['inputs']:
   p=root/x['path'];p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/x['path'],p)
  for n in names:(root/rel/'artifacts'/n).unlink(missing_ok=True)
  for program in ['run.py','validate.py']:subprocess.run([sys.executable,str(root/rel/'src'/program)],cwd=root,check=True,stdout=subprocess.DEVNULL)
  exact={n:sha(D/'artifacts'/n)==sha(root/rel/'artifacts'/n) for n in names};assert all(exact.values()),exact
  print(json.dumps({'status':'PASS','byte_exact':exact,'scope':'Fixed native-cache/prefix-capacity accounting; no meanings, source identity or native alphabet established.'},sort_keys=True))
if __name__=='__main__':main()
