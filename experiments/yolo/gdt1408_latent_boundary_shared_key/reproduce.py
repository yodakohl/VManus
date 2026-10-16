#!/usr/bin/env python3
"""Reproduce the bounded control stop in isolation; never invoke native fitting."""
from pathlib import Path
import json,shutil,subprocess,sys,tempfile
B=Path(__file__).resolve().parent;R=B.parents[2];rel=B.relative_to(R)
lock=json.loads((B/'LOCK.json').read_text())
with tempfile.TemporaryDirectory(prefix='gdt1408-control-replay-') as temporary:
 sandbox=Path(temporary)
 for name in list(lock['files'])+[str(rel/'LOCK.json')]:
  target=sandbox/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/name,target)
 target=sandbox/rel;(target/'artifacts').mkdir(exist_ok=True)
 primary=subprocess.run([sys.executable,str(target/'src/run.py'),'--controls'],capture_output=True,text=True)
 assert primary.returncode==0,'control executable error'
 control=json.loads((target/'artifacts/CONTROLS.json').read_text());generated=json.loads((target/'artifacts/GENERATED_CONTROL.json').read_text())
 assert control['status']=='STOP_GENERATED_CONTROL_NOT_RECOVERED' and generated['result']['status']=='UNKNOWN'
 refusal=subprocess.run([sys.executable,str(target/'src/validate.py'),'--gate'],capture_output=True,text=True)
 assert refusal.returncode!=0 and 'AssertionError' in refusal.stderr and "assert generated['result']['status']=='SAT'" in refusal.stderr
 assert all(not(target/'artifacts'/n).exists() for n in ['NATIVE_INPUT.json','RESULT.json','GATE_VALIDATION.json'])
 print(json.dumps({'status':'PASS_EXPECTED_CONTROL_STOP_REPRODUCED','primary_control_gate':control['status'],'cap_reason':generated['result']['reason'],'independent_gate_refused':True,'native_not_run':True,'scope':'Stop reproduced, not a passed research gate or a cipher rejection. Timed caps need not stop at identical operation counts on different machines.'}))
