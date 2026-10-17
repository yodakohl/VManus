#!/usr/bin/env python3
"""Fixed INITIAL/REST lift with unchanged Boolean solver; one full native case."""
import argparse,hashlib,importlib.util,json,time
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2];A=E/'artifacts'
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def module(p):
 sp=importlib.util.spec_from_file_location('gdt1428_frozen_boolean',ROOT/p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m

def save(name,obj):
 p=A/name;assert not p.exists(),name;p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def config():
 for p,h in read(E/'LOCK.json')['files'].items():assert sha(ROOT/p)==h,p
 s=read(E/'src/SPEC.json')
 for p,h in s['predecessor_sha256'].items():assert sha(ROOT/p)==h,p
 assert s['mode']=='FWD' and len(s['signs'])==22
 return s

def role_fixtures(engine,caps):
 cases=[(['aa','bb'],[['a','o'],['o','a']],'SAT'),(['aaa'],[['a','o','o']],'SAT'),(['aaa'],[['a','o','e']],'UNSAT'),(['abc'],[['a','o','o']],'SAT')];out=[]
 for ws,groups,expected in cases:
  alpha=sorted(set(''.join(ws)));enc={(c,j):chr(0xE000+2*alpha.index(c)+j) for c in alpha for j in [0,1]}
  W=[''.join(enc[c,int(i>0)] for i,c in enumerate(w)) for w in ws];r=engine.solve(groups,W,['a','o','e'],'FWD',caps)
  if r['status']=='SAT':
   assert all(w in W for w in r['words']);assert [[r['key'][c] for c in w] for w in r['words']]==groups
  out.append({'source_words':ws,'groups':groups,'expected':expected,'result':r})
 return {'status':'PASS' if all(x['result']['status']==x['expected'] for x in out) else 'STOP','cases':out,'scope':'Source-free genuine I/R distinction, overlap, merging and REST consistency; no native evidence.'}
def annotate(result,lift):
 if result['status']!='SAT':return result
 inv={code:w for w,code in lift['pairs']};words=result.get('words',result.get('source_words'));result['decoded_source_words']=[inv[w] for w in words]
 result['keys_by_position']={role:{d['source_letter']:result['key'][d[role]] for d in lift['letter_lift'] if d[role] in result['key']} for role in ['INITIAL','REST']};return result

def solve(kind):
 s=config();source=read(ROOT/s['source_projection']);lift=read(ROOT/s['role_projection']);W=lift['words'];assert len(W)==2133 and len(source['alphabet'])==23
 path=ROOT/s['control_input' if kind=='gate' else 'native_input'];inp=read(path);groups=inp['groups'];assert len(groups)==s['control_groups' if kind=='gate' else 'native_groups']
 if kind=='native':
  gate=read(A/'GATE_VALIDATION.json')
  if gate['status']!='PASS':
   save('NATIVE_STOP.json',{'status':'CONTROL_STOP_NO_NATIVE_TEST','native_cases_executed':0,'gate_sha256':sha(A/'GATE_VALIDATION.json')});print('CONTROL_STOP_NO_NATIVE_TEST');return
 engine=module(s['primary_engine']);fixtures=role_fixtures(engine,s['primary_search']) if kind=='gate' else None
 t=time.monotonic();executed=fixtures is None or fixtures['status']=='PASS'
 # No planted key, aligned control words or source adjacency enter solve.
 result=engine.solve(groups,W,s['signs'],s['mode'],s['primary_search']) if executed else {'status':'UNKNOWN','reason':'ROLE_FIXTURE_STOP'}
 elapsed=time.monotonic()-t;annotate(result,lift)
 out={'experiment_id':'GDT1428','status':result['status'],'result':result,'elapsed_seconds':elapsed,'input_sha256':sha(path),'role_projection_sha256':sha(ROOT/s['role_projection']),'source_projection_sha256':sha(ROOT/s['source_projection']),'lock_sha256':sha(E/'LOCK.json')}
 if kind=='gate':out.update(role_fixtures=fixtures,actual_source_search_executed=executed)
 else:out['gate_sha256']=sha(A/'GATE_VALIDATION.json')
 save('CONTROL_PRIMARY.json' if kind=='gate' else 'RESULT.json',out)
 print(json.dumps({'phase':kind,'primary_status':result['status'],'elapsed_seconds':elapsed,'reason':result.get('reason'),'stats':result.get('stats')}),flush=True)
def main():
 p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True)
 for phase in ['gate','native']:g.add_argument('--'+phase,action='store_true')
 a=p.parse_args();solve('gate' if a.gate else 'native')
if __name__=='__main__':main()
