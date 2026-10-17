#!/usr/bin/env python3
"""Complete finite exception masks, unchanged lexical Boolean engine, no meanings."""
import argparse,hashlib,importlib.util,itertools,json,time
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2];A=E/'artifacts'
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def module(name,path):
 sp=importlib.util.spec_from_file_location(name,ROOT/path);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m

def save(name,obj):
 p=A/name;assert not p.exists(),name;p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def config():
 for p,h in read(E/'LOCK.json')['files'].items():assert sha(ROOT/p)==h,p
 s=read(E/'src/SPEC.json')
 for p,h in s['predecessor_sha256'].items():assert sha(ROOT/p)==h,p
 return s

def count(mark,group):
 if not group or len(group)%2:return None
 n=len(group)//2
 return n if list(mark)*n==list(group) else None

def fixtures(s):
 rows=[dict(x,actual=count(x['mark'],x['group'])) for x in s['numeric_fixtures']]
 fields=[count(['d','y'],g) for g in [['d','y'],['d','y']]];joined=count(['d','y'],['d','y','d','y'])
 return {'status':'PASS' if all(x['actual']==x['expected'] for x in rows) and fields==[1,1] and joined==2 else 'STOP','cases':rows,'separate_fields':fields,'joined_field':joined}
def inherited(s):
 old=module('gdt1429_old_static_validator',s['old_lexical_validator']);old.setup();os=read(ROOT/s['old_spec']);_,W,c,n=old.inputs(os);gate=old.gate_report(os,W,c)
 assert gate==read(ROOT/s['inherited_gate']) and gate['status']=='PASS'
 assert read(ROOT/s['inherited_validation'])['status'].startswith('PASS')
 assert read(ROOT/s['native_primary'])['status']==read(ROOT/s['native_independent'])['status']=='UNSAT'
 return W,n

def gate():
 s=config();W,n=inherited(s);f=fixtures(s);save('GATE_PRIMARY.json',{'status':f['status'],'fixtures':f,'inherited_gate_sha256':sha(ROOT/s['inherited_gate']),'inherited_validation_sha256':sha(ROOT/s['inherited_validation']),'actual_source_controls_rerun':False,'words':len(W),'groups':len(n['groups'])});print(json.dumps({'gate_primary':f['status'],'actual_source_controls_rerun':False}),flush=True)
def prepare():
 s=config();n=read(ROOT/s['native_input']);groups=n['groups'];classes={};cases=[];allmarks=[]
 for mark in itertools.product(s['signs'],repeat=2):
  nums=tuple(i for i,g in enumerate(groups) if count(mark,g) is not None)
  if nums not in classes:
   ident='C'+str(len(cases)).zfill(3);classes[nums]=ident;cases.append({'id':ident,'numeric_positions_zero_based':list(nums),'lexical_positions_zero_based':[i for i in range(len(groups)) if i not in nums],'marks':[]})
  ident=classes[nums];case=next(c for c in cases if c['id']==ident);case['marks'].append(list(mark));allmarks.append({'mark':list(mark),'case_id':ident,'numeric_positions_zero_based':list(nums)})
 assert len(allmarks)==484 and sum(len(c['marks']) for c in cases)==484
 save('CASES.json',{'cases':cases,'all_marks':allmarks,'mark_count':484,'native_input_sha256':sha(ROOT/s['native_input']),'baseline_case_id':classes.get(()),'scope':'Maximally numeric necessary masks; no actual numeric classification.'});print(json.dumps({'marks':484,'distinct_lexical_packets':len(cases),'new_packets':sum(bool(c['numeric_positions_zero_based']) and bool(c['lexical_positions_zero_based']) for c in cases)}),flush=True)
def native():
 s=config();assert read(A/'GATE_VALIDATION.json')['status']=='PASS';W,n=inherited(s);engine=module('gdt1429_old_boolean',s['primary_engine']);cases=read(A/'CASES.json')['cases'];out=[]
 for c in cases:
  ids=c['lexical_positions_zero_based'];gs=[n['groups'][i] for i in ids];t=time.monotonic()
  if not c['numeric_positions_zero_based']:
   r=read(ROOT/s['native_primary'])['result'];origin='INHERITED_1428_DUAL_UNSAT'
  elif not ids:
   r={'status':'SAT','key':{u:s['signs'][0] for u in set(''.join(W))},'words':[],'directions':[],'reason':'NO_LEXICAL_OBLIGATIONS'};origin='ALL_NUMERIC_NO_SEARCH'
  else:r=engine.solve(gs,W,s['signs'],'FWD',s['primary_search']);origin='NEW_LEXICAL_SEARCH'
  out.append({'case_id':c['id'],'status':r['status'],'origin':origin,'result':r,'elapsed_seconds':time.monotonic()-t})
  print(json.dumps({'case':c['id'],'status':r['status'],'origin':origin}),flush=True)
 save('RESULT.json',{'experiment_id':'GDT1429','cases':out,'case_input_sha256':sha(A/'CASES.json'),'native_input_sha256':sha(ROOT/s['native_input']),'gate_sha256':sha(A/'GATE_VALIDATION.json')})
def main():
 p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True)
 for phase in ['gate','prepare','native']:g.add_argument('--'+phase,action='store_true')
 a=p.parse_args()
 if a.gate:gate()
 elif a.prepare:prepare()
 else:native()
if __name__=='__main__':main()
