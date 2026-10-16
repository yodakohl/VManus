#!/usr/bin/env python3
"""Byte comparison in an isolated tree containing only locked inputs."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys,tempfile
D=Path(__file__).resolve().parents[1]
R=D.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 lock=json.loads((D/'LOCK.json').read_text())
 names=['SOURCE.json','RESULT.json','TRACE_77.json','PRIMARY_CONTROLS.json','INDEPENDENT_CONTROLS.json','VALIDATION.json']
 with tempfile.TemporaryDirectory(prefix='vmanus1407replay_') as tmp:
  root=Path(tmp);rel=D.relative_to(R)
  shutil.copytree(D,root/rel,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
  for item in lock['entries']:
   out=root/item['path'];out.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/item['path'],out)
  for name in names:(root/rel/'artifacts'/name).unlink(missing_ok=True)
  for script in ['run.py','validate.py']:
   subprocess.run([sys.executable,str(root/rel/'src'/script)],cwd=root,check=True,stdout=subprocess.DEVNULL)
  matched={name:sha(D/'artifacts'/name)==sha(root/rel/'artifacts'/name) for name in names}
  assert all(matched.values()),matched
  print(json.dumps({'status':'PASS','byte_exact':matched,'scope':'Only the fixed overt indexed-construction/source accounting; no meanings.'},sort_keys=True))
if __name__=='__main__':main()

