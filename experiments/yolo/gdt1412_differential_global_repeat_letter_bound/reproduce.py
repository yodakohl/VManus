#!/usr/bin/env python3
"""Replay fixed native-panel/source-vocabulary bounds from cached pinned inputs."""
from pathlib import Path
import json,shutil,subprocess,sys,tempfile
B=Path(__file__).resolve().parent;R=B.parents[2];relative=B.relative_to(R)
lock=json.loads((B/'LOCK.json').read_text())
missing=[n for n in lock['files'] if not (R/n).is_file()]
assert not missing,('Required existing GDT001 language packs or cached research inputs missing; prepare using original hash-pinned public provenance/recipe.',missing)
with tempfile.TemporaryDirectory(prefix='gdt1412-repeat-bound-') as directory:
 root=Path(directory)
 for name in list(lock['files'])+[str(relative/'LOCK.json')]:
  p=root/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/name,p)
 target=root/relative;(target/'artifacts').mkdir(exist_ok=True)
 for args in [['src/run.py','--controls'],['src/run.py'],['src/validate.py','--validate']]:
  process=subprocess.run([sys.executable,str(target/args[0]),*args[1:]],capture_output=True,text=True)
  assert process.returncode==0,('replay_command_failed',args,process.stderr[-1600:])
 names=['CONTROLS.json','NATIVE_PANEL.json','VOCABULARY_RUNS.json','RESULT.json','VALIDATION.json']
 for name in names:assert (target/'artifacts'/name).read_bytes()==(B/'artifacts'/name).read_bytes(),name
 print(json.dumps({'status':'PASS_BYTE_EXACT_ISOLATED_REPLAY','artifacts':names,'scope':'Fixed source/native necessary capacity only; no wordmeaning or actual offset identification.'}))
