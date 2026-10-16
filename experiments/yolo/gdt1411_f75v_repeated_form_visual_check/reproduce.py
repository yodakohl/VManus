#!/usr/bin/env python3
"""Replay only frozen observation accounting, not AI perception."""
from pathlib import Path
import json,shutil,subprocess,sys,tempfile
B=Path(__file__).resolve().parent;R=B.parents[2];relative=B.relative_to(R)
lock=json.loads((B/'CODE_LOCK.json').read_text())
with tempfile.TemporaryDirectory(prefix='gdt1411-accounting-') as directory:
 root=Path(directory)
 for name in list(lock['files'])+[str(relative/'CODE_LOCK.json')]:
  p=root/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/name,p)
 target=root/relative
 for script in ['src/run.py','src/validate.py']:
  process=subprocess.run([sys.executable,str(target/script)],capture_output=True,text=True)
  assert process.returncode==0,('replay_command_failed',script,process.stderr[-1200:])
 names=['CONTROLS.json','RESULT.json','VALIDATION.json']
 for name in names:assert (target/'artifacts'/name).read_bytes()==(B/'artifacts'/name).read_bytes(),name
 print(json.dumps({'status':'PASS_BYTE_EXACT_ACCOUNTING_REPLAY','artifacts':names,'scope':'Replays saved judgments only; does not reproduce or validate perception.'}))
