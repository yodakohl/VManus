#!/usr/bin/env python3
"""Gated necessary-core test; no new controls or native decoder."""
import concurrent.futures,hashlib,json,subprocess,sys
from pathlib import Path
E=Path(__file__).resolve().parent;ROOT=E.parents[2]
def invoke(script,mode):subprocess.run([sys.executable,str(E/script),mode],cwd=ROOT,check=True)
def read(n):return json.loads((E/'artifacts'/n).read_text())
def sha(n):return hashlib.sha256((E/'artifacts'/n).read_bytes()).hexdigest()
def both(mode):
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as p:list(p.map(lambda x:invoke(x,mode),['src/run.py','src/validate.py']))
def main():
 both('--gate');p=read('CONTROL_SUBSET.json');q=read('INDEPENDENT_CONTROL.json');passed=p['status']==q['status']=='PASS'
 x={'status':'PASS' if passed else 'STOP','primary_control_sha256':sha('CONTROL_SUBSET.json'),'independent_control_sha256':sha('INDEPENDENT_CONTROL.json'),'claim':'ANYverifiedordinaryforwardkey on unchangedoldcontrolsubset; no plaintextrecoveryclaim for this relaxation.'}
 out=E/'artifacts/GATE_VALIDATION.json'
 if out.exists():assert json.loads(out.read_text())==x
 else:out.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
 if passed:both('--native')
 else:print(json.dumps({'native':'NOT_EXECUTED_FIXED_CONTROL_STOP'}),flush=True)
 invoke('src/validate.py','--validate')
if __name__=='__main__':main()
