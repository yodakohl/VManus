#!/usr/bin/env python3
"""Independent no-edge certificates and exact pinned old DFS, never primary import."""
import argparse,hashlib,importlib.util,json,time
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2];A=E/'artifacts'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,x):
 p=A/n
 if p.exists():assert read(p)==x,'Refuse changed overwrite '+n
 else:p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def setup():
 s=read(E/'src/SPEC.json');pins=read(E/'LOCK.json')['files']
 if isinstance(pins,dict):
  for p,h in pins.items():assert sha(ROOT/p)==h,p
 else:
  for p in pins:assert sha(ROOT/p['path'])==p['sha256'],p['path']
 for p,h in s['predecessor_sha256'].items():assert sha(ROOT/p)==h,p
 assert s['mode']=='FWD' and s['native_groups']==59 and s['control_groups']==32 and len(s['signs'])==len(set(s['signs']))==22
 assert s['independent_search']=={'seconds_per_case':20,'nodes_cap':250000,'checks_cap':5000000}
 return s

def original_inputs(s):
 source=read(ROOT/s['source_projection']);records=source['records'];W=sorted({w for r in records for w in r['words']});alpha=sorted(set(''.join(W)))
 assert W==source['words'] and alpha==source['alphabet'] and len(W)==2133 and len(alpha)==23
 assert sum(len(r['words']) for r in records)==5768 and len(records)==346
 control=read(ROOT/s['control_input']);idx=next(i for i,r in enumerate(records) if len(r['words'])>=32);r=records[idx]
 assert control['source_record_index']==idx and control['source_body_child_index']==r['body_child_index']
 ws=r['words'][:32];key={c:s['signs'][i%s['control_mapping_modulo']] for i,c in enumerate(alpha)};gs=[[key[c] for c in w] for w in ws]
 assert control['planted_words']==ws and control['planted_key']==key and control['groups']==gs
 assert control['source_projection_sha256']==sha(ROOT/s['source_projection'])
 active=set(''.join(ws));classes={}
 for c in alpha:
  if c in active:classes.setdefault(key[c],[]).append(c)
 assert control['active_collision_classes']==[cs for cs in classes.values() if len(cs)>1]
 native=read(ROOT/s['native_input']);assert native['edition']=='IT2a' and native['group_count']==59
 old=read(ROOT/native['source']);assert sha(ROOT/native['source'])==native['source_sha256']
 rows=[r for r in old['groups'] if r['edition']=='IT2a'];assert len(rows)==59
 assert native['ids']==[r['group']['source_group_id'] for r in rows]
 assert native['raw_groups']==[r['group']['ivtff_group_raw'] for r in rows]
 assert native['loci']==[r['locus'] for r in rows]
 units=[];signs=sorted(s['signs'],key=lambda v:(-len(v),v))
 for raw in native['raw_groups']:
  pos=0;u=[]
  while pos<len(raw):
   v=next((v for v in signs if raw.startswith(v,pos)),None);assert v is not None
   u.append(v);pos+=len(v)
  units.append(u)
 assert units==native['groups']
 return source,W,control,native

def backend_cert(result,groups,W,signs):
 assert result['status']=='SAT';key=result['key'];ws=result.get('words',result.get('source_words'));ds=result['directions']
 assert set(key)==set(''.join(W)) and all(v in signs for v in key.values())
 assert len(ws)==len(ds)==len(groups)
 for w,d,g in zip(ws,ds,groups):assert w in W and d=='FWD' and [key[c] for c in w]==g

def inputs(s):
 source,W,oldcontrol,native=original_inputs(s)
 proj=read(ROOT/s['direction_projection']);expected=[[w,w[::-1]] for w in W]
 assert proj['source_projection_sha256']==sha(ROOT/s['source_projection']) and proj['pairs']==expected
 reversedW=sorted(w[::-1] for w in W)
 assert len(set(reversedW))==len(W)==2133 and proj['words']==reversedW and proj['alphabet']==source['alphabet']
 control=read(ROOT/s['reverse_control_input'])
 assert control['direction']=='GLOBAL_REVERSE' and control['parent_control_sha256']==sha(ROOT/s['control_input'])
 assert control['source_words']==oldcontrol['planted_words'] and control['planted_key']==oldcontrol['planted_key']
 assert control['groups']==[list(reversed(g)) for g in oldcontrol['groups']]
 for word,group in zip(control['source_words'],control['groups']):
  assert group==[control['planted_key'][c] for c in word[::-1]]
 c=dict(control,planted_words=[w[::-1] for w in control['source_words']])
 return source,reversedW,c,native

def cert(result,groups,W,signs):
 backend_cert(result,groups,W,signs)
 proj=read(A/'DIRECTION_PROJECTION.json');lookup={view:orig for orig,view in proj['pairs']}
 assert set(W)==set(lookup)
 words=result.get('words',result.get('source_words'))
 for word,group in zip(words,groups):
  original=lookup[word]
  assert word==original[::-1] and group==[result['key'][original[i]] for i in range(len(original)-1,-1,-1)]

def check_wrapper(obj,inputpath):
 assert obj['input_sha256']==sha(inputpath)
 status=obj['result']['status'];assert status in ['SAT','UNSAT','UNKNOWN']
 # Root wrappers may expose raw solver status or gate PASS/STOP; decisions below use result.
 assert obj['status'] in [status,'PASS' if status=='SAT' else 'STOP']

def search(s,groups,W):
 path=ROOT/s['independent_engine'];assert sha(path)==s['predecessor_sha256'][s['independent_engine']]
 module=importlib.util.spec_from_file_location('fixed1421dfs',path);m=importlib.util.module_from_spec(module);module.loader.exec_module(m)
 start=time.monotonic();r=m.solve(groups,W,s['signs'],'FWD',s['independent_search']);elapsed=time.monotonic()-start
 if r['status']=='SAT':cert(r,groups,set(W),s['signs'])
 return r,elapsed

def gate_report(s,W,control):
 a=read(A/'CONTROL_PRIMARY.json');b=read(A/'INDEPENDENT_CONTROL.json')
 for z in [a,b]:
  check_wrapper(z,ROOT/s['reverse_control_input'])
  if z['result']['status']=='SAT':cert(z['result'],control['groups'],set(W),s['signs'])
 cert({'status':'SAT','key':control['planted_key'],'words':control['planted_words'],'directions':['FWD']*32},control['groups'],set(W),s['signs'])
 ss=[a['result']['status'],b['result']['status']];invalid='UNSAT' in ss;passed=ss==['SAT','SAT']
 if not passed:assert not (A/'RESULT.json').exists() and not (A/'INDEPENDENT_RESULT.json').exists()
 return {'status':'PASS' if passed else 'STOP','reason':'BOTH_ANY_CERTIFICATES_VERIFIED' if passed else 'INVALID_KNOWN_POSITIVE_UNSAT' if invalid else 'CONTROL_SEARCH_UNKNOWN','known_positive_result_invalid':invalid,'primary_status':ss[0],'independent_status':ss[1],'control_groups':32,'control_input_sha256':sha(ROOT/s['reverse_control_input']),'direction_projection_sha256':sha(ROOT/s['direction_projection']),'primary_sha256':sha(A/'CONTROL_PRIMARY.json'),'independent_sha256':sha(A/'INDEPENDENT_CONTROL.json'),'lock_sha256':sha(E/'LOCK.json'),'validator_sha256':sha(Path(__file__)),'scope':'ANY-key capacity only; planted recovery and uniqueness are not established by this gate.'}

def gate():
 s=setup();_,W,c,_=inputs(s);assert not (A/'INDEPENDENT_CONTROL.json').exists(),'No control rerun'
 assert (A/'CONTROL_PRIMARY.json').exists()
 r,elapsed=search(s,c['groups'],W);save('INDEPENDENT_CONTROL.json',{'status':r['status'],'result':r,'elapsed_seconds':elapsed,'input_sha256':sha(ROOT/s['reverse_control_input'])})
 g=gate_report(s,W,c);save('GATE_VALIDATION.json',g);print(json.dumps(g))

def native():
 s=setup();_,W,c,n=inputs(s);g=gate_report(s,W,c);assert g==read(A/'GATE_VALIDATION.json') and g['status']=='PASS'
 assert not (A/'INDEPENDENT_RESULT.json').exists(),'No native rerun'
 r,elapsed=search(s,n['groups'],W);save('INDEPENDENT_RESULT.json',{'status':r['status'],'result':r,'elapsed_seconds':elapsed,'input_sha256':sha(ROOT/s['native_input'])});print(json.dumps({'independent_status':r['status']}))

def inverses(result,n,W):
 key=result['key'];proj=read(A/'DIRECTION_PROJECTION.json');originals=[z[0] for z in proj['pairs']];lookup={v:w for w,v in proj['pairs']};unique={}
 for g in n['groups']:
  t=tuple(g)
  if t not in unique:unique[t]=[w for w in originals if len(w)==len(g) and [key[c] for c in reversed(w)]==g]
 assert all(unique.values())
 chosen=[lookup[w] for w in result.get('words',result.get('source_words'))]
 positions=[{'source_group_id':i,'locus':l,'raw_group':raw,'units':g,'canonical_words':unique[tuple(g)],'returned_original_word':w,'scientific_direction':'GLOBAL_REVERSE'} for i,l,raw,g,w in zip(n['ids'],n['loci'],n['raw_groups'],n['groups'],chosen)]
 return {'key':key,'returned_original_words':chosen,'distinct_groups':[{'units':list(g),'canonical_words':ws} for g,ws in unique.items()],'positions':positions,'scope':'Full original sourceword preimages for this key under fixed global reversal. FWD backend uses reversed views only. No translation, uniqueness or key preference.'}

def validate():
 s=setup();_,W,c,n=inputs(s);g=gate_report(s,W,c);assert g==read(A/'GATE_VALIDATION.json');inverse={}
 if g['status']!='PASS':
  assert read(A/'NATIVE_STOP.json')['native_cases_executed']==0
  final='INVALID_CONTROL_UNSAT' if g['known_positive_result_invalid'] else 'CONTROL_STOP_NO_NATIVE_SEARCH';statuses={};executed=False
 else:
  a=read(A/'RESULT.json');b=read(A/'INDEPENDENT_RESULT.json');statuses={};executed=True
  for label,z in [('primary',a),('independent',b)]:
   check_wrapper(z,ROOT/s['native_input']);r=z['result'];statuses[label]=r['status']
   if r['status']=='SAT':cert(r,n['groups'],set(W),s['signs']);inverse[label]=inverses(r,n,W)
  ss=set(statuses.values())
  final='INVALID_SOLVER_DISAGREEMENT' if ss=={'SAT','UNSAT'} else 'SAT_CAPACITY_UNASSESSED' if 'SAT' in ss else 'DUAL_UNSAT_GLOBAL_REVERSE' if ss=={'UNSAT'} else 'UNKNOWN_OPEN'
 decision={'status':final,'confirmed_words':0,'native_executed':executed,'native_cases':int(executed),'engine_statuses':statuses,'gate_status':g['status'],'source_projection_sha256':sha(ROOT/s['source_projection']),'native_input_sha256':sha(ROOT/s['native_input']),'lock_sha256':sha(E/'LOCK.json'),'direction':'GLOBAL_REVERSE','direction_projection_sha256':sha(ROOT/s['direction_projection']),'claim_ceiling':s['claim_ceiling']}
 save('FINAL_DECISION.json',decision)
 if inverse:save('INVERSE_WORD_SETS.json',{'status':'UNASSESSED_FULL_PREIMAGE_SETS','source_projection_sha256':sha(ROOT/s['source_projection']),'by_engine':inverse})
 validation={'status':'INVALID_ENGINE_RESULT' if final.startswith('INVALID') else 'PASS_INDEPENDENT_NO_EDGE_CERTIFICATE_ACCOUNTING','validator_sha256':sha(Path(__file__)),'decision_sha256':sha(A/'FINAL_DECISION.json'),'control_gate':g,'native_engine_statuses':statuses,'full_inverse_keys':sorted(inverse),'checks':['Pinned unchanged source W and native59 reconstructed','Original first32 source calibration and jmod20 key/groups independently checked','Both control solver outputs checked separately; no planted truth passed to solver','Every returned SAT key replayed directly on ORIGINAL sourcewords in global reverse codepoint order, with FWD backend views only','Native UNSAT effective only with both exhaustive results; UNKNOWN not a rejection','Each nativeSAT gets all frozen-vocabulary preimages per group and all59sourcepositions'],'limits':['No source adjacency edges, position rows or numeric exemptions; global reversal is additional writing assumption, not required by RTL display.','Raw preimages are unassessed witnesses, not native word meanings; distinct returned keys are not merged.','Only pinned old1421 rowDFS imported; primaryBoolean compiler and currentrun.py not imported.']}
 save('VALIDATION.json',validation);print(json.dumps(decision))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--gate',action='store_true');p.add_argument('--native',action='store_true');p.add_argument('--validate',action='store_true');p.add_argument('--check',action='store_true');a=p.parse_args()
 if a.gate:gate()
 elif a.native:native()
 elif a.validate or a.check:validate()
 else:p.error('choose --gate, --native or --validate/--check')
