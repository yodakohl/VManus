#!/usr/bin/env python3
"""Run fixed control gates before any declared native shared-key evaluation."""
import concurrent.futures,hashlib,json,subprocess,sys
from pathlib import Path
E=Path(__file__).resolve().parent;ROOT=E.parents[2]
def invoke(script,mode):subprocess.run([sys.executable,str(E/script),mode],cwd=ROOT,check=True)
def read(n):return json.loads((E/'artifacts'/n).read_text())
def sha(n):return hashlib.sha256((E/'artifacts'/n).read_bytes()).hexdigest()
def main():
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
  list(pool.map(lambda x:invoke(*x),[('src/run.py','--gate'),('src/validate.py','--gate')]))
 p=read('CONTROL.json');q=read('INDEPENDENT_CONTROL.json')
 passed=p['status']==q['status']=='PASS_EXACT_UNIQUE'
 gate={'status':'PASS' if passed else 'STOP','primary_control_sha256':sha('CONTROL.json'),'independent_control_sha256':sha('INDEPENDENT_CONTROL.json'),'reason':'Both exact32word recoveries and alternate-message UNSAT' if passed else 'A fixed required control condition is absent, ambiguous, invalid or unverified; native evaluation not authorized.'}
 path=E/'artifacts/GATE_VALIDATION.json'
 if path.exists():assert json.loads(path.read_text())==gate
 else:path.write_text(json.dumps(gate,ensure_ascii=False,indent=2)+'\n')
 if passed:
  with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
   list(pool.map(lambda x:invoke(*x),[('src/run.py','--native'),('src/validate.py','--native')]))
 else:print(json.dumps({'native':'NOT_EXECUTED_FIXED_CONTROL_STOP'}),flush=True)
 invoke('src/validate.py','--validate')
if __name__=='__main__':main()
