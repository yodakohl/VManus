"""Isolated exact replay of the inherited-pair logical application."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys,tempfile
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];REL=D.relative_to(ROOT)
lock=json.loads((D/'LOCK.json').read_text());base=Path(tempfile.mkdtemp(prefix='vmanus1401-'))/'repository';base.mkdir()
for p,h in lock['files'].items():
 source=ROOT/p;assert hashlib.sha256(source.read_bytes()).hexdigest()==h,p
 target=base/p;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
shutil.copyfile(D/'LOCK.json',base/REL/'LOCK.json')
for name in ['run.py','validate.py']:
 subprocess.run([sys.executable,str(base/REL/'src'/name)],cwd=base,check=True,stdout=subprocess.DEVNULL)
checks={n:(base/REL/'artifacts'/n).read_bytes()==(D/'artifacts'/n).read_bytes() for n in ['RESULT.json','VALIDATION.json']}
assert all(checks.values()),checks
print(json.dumps({'status':'PASS','byte_exact':checks},indent=2,sort_keys=True))
