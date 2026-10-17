#!/usr/bin/env python3
"""Replay in a fresh temporary tree; never rewrite the registered artifacts."""
import json, shutil, subprocess, tempfile
from pathlib import Path
E=Path(__file__).resolve().parent;ROOT=E.parents[2]
def main():
 lock=json.loads((E/'LOCK.json').read_text())
 with tempfile.TemporaryDirectory(prefix='vmanus1418-replay-') as tmp:
  base=Path(tmp)
  for rel in lock['files']:
   dst=base/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/rel,dst)
  work=base/E.relative_to(ROOT);(work/'artifacts').mkdir(exist_ok=True);shutil.copyfile(E/'LOCK.json',work/'LOCK.json')
  def run(script,flag):subprocess.run(['python3',str(work/'src'/script),flag],check=True,cwd=base)
  run('run.py','--gate');control=json.loads((work/'artifacts/CONTROL.json').read_text())
  if control.get('result',{}).get('status')!='SAT':
   print(json.dumps({'status':'CONTROL_STOP_NO_NATIVE','control':control.get('result',{}).get('status',control.get('status'))}));return
  run('validate.py','--gate');run('run.py','--native');run('validate.py','--native')
  validation=json.loads((work/'artifacts/VALIDATION.json').read_text())
  print(json.dumps({'status':'FRESH_REPLAY_VALIDATED','case_statuses':[{k:c[k] for k in ('source','mode','primary','independent','effective')} for c in validation['cases']],'scope':'Fresh exact contract/certificate checks; wall-cap UNKNOWN may vary. Not deterministic key/message recovery or semantic validation.'}))
if __name__=='__main__':main()
