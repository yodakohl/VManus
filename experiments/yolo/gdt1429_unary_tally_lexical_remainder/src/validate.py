#!/usr/bin/env python3
"""Independent whole-pair membership and inherited lexical certificate checks."""
import argparse,hashlib,importlib.util,itertools,json,time
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2];A=E/'artifacts'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,x):
 p=A/n
 if p.exists():assert read(p)==x,'Refuse changed overwrite '+n
 else:p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def load(p,name):
 z=importlib.util.spec_from_file_location(name,ROOT/p);m=importlib.util.module_from_spec(z);z.loader.exec_module(m);return m

def setup():
 s=read(E/'src/SPEC.json');pins=read(E/'LOCK.json')['files']
 if isinstance(pins,dict):
  for p,h in pins.items():assert sha(ROOT/p)==h,p
 else:
  for p in pins:assert sha(ROOT/p['path'])==p['sha256'],p['path']
 for p,h in s['predecessor_sha256'].items():assert sha(ROOT/p)==h,p
 assert s['independent_search']=={'seconds_per_case':20,'nodes_cap':250000,'checks_cap':5000000}
 old=load(s['old_lexical_validator'],'pinned1428static');ss=old.setup();_,W,c,n=old.inputs(ss)
 assert s['source_projection']==ss['source_projection'] and s['native_input']==ss['native_input'] and s['control_input']==ss['control_input'] and s['role_projection']==ss['role_projection'] and s['signs']==ss['signs']
 assert old.gate_report(ss,W,c)==read(ROOT/s['inherited_gate']) and read(ROOT/s['inherited_gate'])['status']=='PASS'
 assert len(n['groups'])==59
 return s,old,W,c,n

def tally(group,mark):
 if not group or len(group)%2:return None
 pairs=list(zip(group[0::2],group[1::2]))
 return len(pairs) if all(pair==tuple(mark) for pair in pairs) else None

def fixtures(s):
 rows=[]
 for case in s['numeric_fixtures']:
  actual=tally(case['group'],case['mark']);assert actual==case['expected']
  rows.append(dict(case,actual=actual))
 separate=[tally(g,['d','y']) for g in [['d','y'],['d','y']]];joined=tally(['d','y','d','y'],['d','y'])
 assert separate==[1,1] and joined==2
 return {'status':'PASS','cases':rows,'separate_fields':separate,'joined_field':joined}

def baseline(s):
 a=read(ROOT/s['native_primary']);b=read(ROOT/s['native_independent'])
 assert a['result']['status']==b['result']['status']=='UNSAT'
 assert a['input_sha256']==b['input_sha256']==sha(ROOT/s['native_input'])
 return a,b

def gate_report(s,old,W,c,n):
 baseline(s);cases(s,n)
 assert read(ROOT/s['inherited_validation'])['status'].startswith('PASS')
 primary=read(A/'GATE_PRIMARY.json');assert primary['status']=='PASS'
 assert primary['fixtures']==fixtures(s)
 assert primary['inherited_gate_sha256']==sha(ROOT/s['inherited_gate']) and primary['inherited_validation_sha256']==sha(ROOT/s['inherited_validation'])
 assert primary['actual_source_controls_rerun'] is False and primary['words']==2133 and primary['groups']==59
 for p in [s['inherited_gate'],s['inherited_validation'],s['control_primary'],s['control_independent'],s['native_primary'],s['native_independent']]:assert p in s['predecessor_sha256']
 return {'status':'PASS','inherited_positive_controls':'Already executed1428controls/rolefixtures statically replayed; no search rerun','new_numeric_fixtures':fixtures(s),'source_projection_sha256':sha(ROOT/s['source_projection']),'role_projection_sha256':sha(ROOT/s['role_projection']),'native_input_sha256':sha(ROOT/s['native_input']),'case_input_sha256':sha(A/'CASES.json'),'primary_gate_sha256':sha(A/'GATE_PRIMARY.json'),'inherited_gate_sha256':sha(ROOT/s['inherited_gate']),'lock_sha256':sha(E/'LOCK.json'),'validator_sha256':sha(Path(__file__)),'scope':'Capacity prerequisites and bookkeeping only, no native number or word assignment.'}

def gate():
 s,old,W,c,n=setup();save('GATE_VALIDATION.json',gate_report(s,old,W,c,n));print('PASS inherited static gate and fixed numeric fixtures')

def cases(s,n):
 saved=read(A/'CASES.json');assert saved['native_input_sha256']==sha(ROOT/s['native_input']) and saved['mark_count']==484
 masks={};expected=[];all_marks=[]
 for mark in itertools.product(s['signs'],repeat=2):
  nums=tuple(i for i,g in enumerate(n['groups']) if tally(g,mark) is not None)
  if nums not in masks:
   masks[nums]=len(expected);expected.append({'id':f'C{len(expected):03d}','numeric_positions_zero_based':list(nums),'lexical_positions_zero_based':[i for i in range(59) if i not in nums],'marks':[]})
  expected[masks[nums]]['marks'].append(list(mark))
  all_marks.append({'mark':list(mark),'case_id':expected[masks[nums]]['id'],'numeric_positions_zero_based':list(nums)})
 assert saved['cases']==expected
 assert saved['all_marks']==all_marks and len(all_marks)==484
 assert saved['baseline_case_id']==expected[masks[()]]['id']
 assert sum(len(z['marks']) for z in expected)==484
 return expected

def native():
 s,old,W,c,n=setup();assert gate_report(s,old,W,c,n)==read(A/'GATE_VALIDATION.json');cs=cases(s,n)
 assert not (A/'INDEPENDENT_RESULT.json').exists(),'No search reruns'
 engine=load(s['independent_engine'],'pinned1421dfs');base=baseline(s)[1]['result'];out=[]
 for case in cs:
  ids=case['lexical_positions_zero_based'];gs=[n['groups'][i] for i in ids]
  if not case['numeric_positions_zero_based']:r=base;origin='INHERITED_1428_DUAL_UNSAT';elapsed=0.0
  elif not ids:r={'status':'SAT','key':{ch:s['signs'][0] for ch in set(''.join(W))},'source_words':[],'directions':[]};origin='ALL_NUMERIC_NO_SEARCH';elapsed=0.0
  else:
   start=time.monotonic();r=engine.solve(gs,W,s['signs'],'FWD',s['independent_search']);elapsed=time.monotonic()-start;origin='NEW_LEXICAL_SEARCH'
  if r['status']=='SAT':old.cert(r,gs,set(W),s['signs'])
  out.append({'case_id':case['id'],'status':r['status'],'origin':origin,'result':r,'elapsed_seconds':elapsed})
 save('INDEPENDENT_RESULT.json',{'cases':out,'native_input_sha256':sha(ROOT/s['native_input']),'cases_sha256':sha(A/'CASES.json'),'validator_sha256':sha(Path(__file__))});print(json.dumps([(z['case_id'],z['status']) for z in out]))

def all_preimages(r,n,s):
 role=read(ROOT/s['role_projection']);words=[p[0] for p in role['pairs']];alpha=sorted(set(''.join(words)));key=r['key'];slot={ch:i for i,ch in enumerate(alpha)};bygroup={}
 for g in n['groups']:
  t=tuple(g)
  if t not in bygroup:bygroup[t]=[w for w in words if len(w)==len(g) and [key[chr(0xE000+2*slot[ch]+int(i>0))] for i,ch in enumerate(w)]==g]
 return bygroup,dict((lift,orig) for orig,lift in role['pairs'])

def validate():
 s,old,W,c,n=setup();assert read(A/'GATE_VALIDATION.json')==gate_report(s,old,W,c,n);cs=cases(s,n);p=read(A/'RESULT.json');q=read(A/'INDEPENDENT_RESULT.json');aa={z['case_id']:z for z in p['cases']};bb={z['case_id']:z for z in q['cases']}
 assert p['experiment_id']=='GDT1429' and p['case_input_sha256']==sha(A/'CASES.json') and p['native_input_sha256']==sha(ROOT/s['native_input']) and p['gate_sha256']==sha(A/'GATE_VALIDATION.json')
 assert q['native_input_sha256']==sha(ROOT/s['native_input']) and q['cases_sha256']==sha(A/'CASES.json')
 assert len(aa)==len(bb)==len(p['cases'])==len(q['cases'])==len(cs) and set(aa)==set(bb)=={z['id'] for z in cs}
 decisions=[];typed=[];inverse=[]
 for case in cs:
  cid=case['id'];ids=case['lexical_positions_zero_based'];nums=case['numeric_positions_zero_based'];gs=[n['groups'][i] for i in ids];states=[]
  for label,entry in [('primary',aa[cid]),('independent',bb[cid])]:
   r=entry['result'];status=r['status'];assert entry['status']==status and status in ['SAT','UNSAT','UNKNOWN'];states.append(status)
   origin='INHERITED_1428_DUAL_UNSAT' if not nums else 'ALL_NUMERIC_NO_SEARCH' if not ids else 'NEW_LEXICAL_SEARCH';assert entry['origin']==origin
   if not nums:
    assert status=='UNSAT'
    assert r==read(ROOT/s['native_primary' if label=='primary' else 'native_independent'])['result']
   if not ids:assert status=='SAT'
   if status=='SAT':
    old.cert(r,gs,set(W),s['signs']);pre,decode=all_preimages(r,n,s);chosen=r.get('words',r.get('source_words'));chosen_by_pos=dict(zip(ids,chosen))
    for mark in case['marks']:
     positions=[];invpos=[]
     for i,g in enumerate(n['groups']):
      count=tally(g,mark);assert (count is not None)==(i in nums)
      common={'position_zero_based':i,'source_group_id':n['ids'][i],'raw_group':n['raw_groups'][i],'units':g}
      if count is not None:positions.append(dict(common,branch='COUNT_ASSUMED',count=count,mark=mark))
      else:
       w=decode[chosen_by_pos[i]];assert w in pre[tuple(g)];positions.append(dict(common,branch='WORD_UNASSESSED',source_word=w))
      invpos.append(dict(common,original_word_preimages=pre[tuple(g)],optional_count=count))
     typed.append({'engine':label,'case_id':cid,'mark':mark,'key':r['key'],'positions':positions,'scope':'Maximally numeric structural witness; no number/word preference.'})
     inverse.append({'engine':label,'case_id':cid,'mark':mark,'key':r['key'],'positions':invpos})
  effective='INVALID_DISAGREEMENT' if set(states)=={'SAT','UNSAT'} else 'SAT_CAPACITY_UNASSESSED' if 'SAT' in states else 'DUAL_UNSAT' if states==['UNSAT','UNSAT'] else 'UNKNOWN_OPEN'
  decisions.append({'case_id':cid,'marks':case['marks'],'numeric_positions_zero_based':nums,'lexical_positions_zero_based':ids,'primary':states[0],'independent':states[1],'effective':effective})
 outcomes={z['effective'] for z in decisions};final='INVALID_DISAGREEMENT' if 'INVALID_DISAGREEMENT' in outcomes else 'SAT_CAPACITY_UNASSESSED' if 'SAT_CAPACITY_UNASSESSED' in outcomes else 'ALL_MARK_CASES_EXCLUDED' if outcomes=={'DUAL_UNSAT'} else 'UNKNOWN_OPEN'
 save('FINAL_DECISION.json',{'status':final,'confirmed_words':0,'mark_count':484,'class_count':len(cs),'cases':decisions,'native_input_sha256':sha(ROOT/s['native_input']),'lock_sha256':sha(E/'LOCK.json')})
 if typed:save('FULL_TYPED_CANDIDATES.json',{'status':'UNASSESSED_MAXIMALLY_NUMERIC_WITNESSES','candidates':typed});save('INVERSE_WORD_SETS.json',{'status':'UNASSESSED_WORD_AND_COUNT_ALTERNATIVES','cases':inverse})
 save('VALIDATION.json',{'status':'INVALID_ENGINE_DISAGREEMENT' if final=='INVALID_DISAGREEMENT' else 'PASS_INDEPENDENT_MEMBERSHIP_AND_CERTIFICATE_ACCOUNTING','validator_sha256':sha(Path(__file__)),'primary_sha256':sha(A/'RESULT.json'),'independent_sha256':sha(A/'INDEPENDENT_RESULT.json'),'cases_sha256':sha(A/'CASES.json'),'decision_sha256':sha(A/'FINAL_DECISION.json'),'marks':484,'classes':len(cs),'source_positions':59,'limits':['Inherited1428positive controls statically replayed, not rerun or new evidence.','Whole-group membership only; original59positions retained in every typed witness.','Every returnedSAT lexical key checked through originalsourceletter/INITIAL/REST semantics; allwordpreimages also retained at numeric positions.','Distinct marks/keys/cases stay separate; no numeric ownership, semantic reading, language or translatedword selected.']});print(final)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--gate',action='store_true');p.add_argument('--native',action='store_true');p.add_argument('--validate',action='store_true');p.add_argument('--check',action='store_true');a=p.parse_args()
 if a.gate:gate()
 elif a.native:native()
 elif a.validate or a.check:validate()
 else:p.error('choose --gate,--native,--validate/--check')
