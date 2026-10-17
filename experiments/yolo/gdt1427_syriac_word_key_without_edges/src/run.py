#!/usr/bin/env python3
"""One vocabulary-only forward case using unchanged GDT1424 Boolean search."""
import argparse,hashlib,importlib.util,json,time
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2];A=E/'artifacts'
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def module(p):
 sp=importlib.util.spec_from_file_location('gdt1427_frozen_boolean',ROOT/p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m

def save(name,obj):
 p=A/name;assert not p.exists(),name;p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def config():
 for p,h in read(E/'LOCK.json')['files'].items():assert sha(ROOT/p)==h,p
 s=read(E/'src/SPEC.json')
 for p,h in s['predecessor_sha256'].items():assert sha(ROOT/p)==h,p
 assert s['mode']=='FWD' and len(s['signs'])==22
 return s

def solve(kind):
 s=config();source=read(ROOT/s['source_projection']);W=source['words'];assert W==sorted(set(W)) and len(W)==2133
 assert sorted(set(''.join(W)))==source['alphabet'] and len(source['alphabet'])==23
 path=ROOT/s['control_input' if kind=='gate' else 'native_input'];inp=read(path);groups=inp['groups']
 assert len(groups)==s['control_groups' if kind=='gate' else 'native_groups']
 if kind=='native':
  gate=read(A/'GATE_VALIDATION.json')
  if gate['status']!='PASS':
   save('NATIVE_STOP.json',{'status':'CONTROL_STOP_NO_NATIVE_TEST','native_cases_executed':0,'gate_sha256':sha(A/'GATE_VALIDATION.json')});print('CONTROL_STOP_NO_NATIVE_TEST');return
 t=time.monotonic()
 # No source words aligned to groups, planted key or bigram edges enter solve.
 result=module(s['primary_engine']).solve(groups,W,s['signs'],s['mode'],s['primary_search'])
 elapsed=time.monotonic()-t
 out={'experiment_id':'GDT1427','status':result['status'],'result':result,'elapsed_seconds':elapsed,'input_sha256':sha(path),'source_projection_sha256':sha(ROOT/s['source_projection']),'lock_sha256':sha(E/'LOCK.json')}
 if kind=='native':out['gate_sha256']=sha(A/'GATE_VALIDATION.json')
 save('CONTROL_PRIMARY.json' if kind=='gate' else 'RESULT.json',out)
 print(json.dumps({'phase':kind,'primary_status':result['status'],'elapsed_seconds':elapsed,'reason':result.get('reason'),'stats':result.get('stats')}),flush=True)
def main():
 p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True)
 for phase in ['gate','native']:g.add_argument('--'+phase,action='store_true')
 a=p.parse_args();solve('gate' if a.gate else 'native')
if __name__=='__main__':main()
