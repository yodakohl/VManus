#!/usr/bin/env python3
"""Independent no-edge forward-function SMT and source accounting."""
import argparse,gzip,hashlib,itertools,json,concurrent.futures
from pathlib import Path
import z3
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2];A=E/'artifacts'
def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,x):
 p=A/n
 if p.exists():assert read(p)==x
 else:p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def keep(us):return bool(us) and not any(a==b and a in ('e','i') for a,b in zip(us,us[1:])) and us[-2:]!=['d','y']
def setup():
 for p,h in read(E/'LOCK.json')['files'].items():assert sha(ROOT/p)==h,p
 return read(E/'src/SPEC.json')
def vocab(s):
 a=read(ROOT/s['recipe_path']);b=read(ROOT/s['deot_path']);c=read(ROOT/s['other_path']);out={}
 for n in s['source_names']:
  if n in ('b4','w1','bs1','gr1'):ws=[w for r in a[n] for w in r['words']]
  elif n=='deot':ws=[w for r in b['source_sections'] for w in r['words']]
  else:
   rows=c[n]['PRIMARY']['units'];assert len(rows)==8000;ws=[r['unit'] for r in rows]
  assert all(isinstance(w,str) and w for w in ws);out[n]=sorted(set(ws))
 return out
def partial(w,us):
 if len(w)!=len(us):return None
 d={}
 for c,u in zip(w,us):
  if c in d and d[c]!=u:return None
  d[c]=u
 return d
def certificate(r,groups,W,signs,mode):
 assert set(r['key'])==set(''.join(W)) and all(v in signs for v in r['key'].values())
 assert len(r['words'])==len(r['directions'])==len(groups)
 for us,w,d in zip(groups,r['words'],r['directions']):
  assert w in W and d in (['FWD'] if mode=='FWD' else ['FWD','REV'])
  text=w if d=='FWD' else w[::-1];assert [r['key'][c] for c in text]==us
def solve(groups,W,signs,mode,seconds):
 alpha=sorted(set(''.join(W)));f={c:z3.Int('f'+str(i)) for i,c in enumerate(alpha)};ui={u:i for i,u in enumerate(signs)}
 solver=z3.Solver();solver.set(timeout=int(seconds*1000))
 for v in f.values():solver.add(v>=0,v<len(signs))
 tables=[];choices=[]
 for i,us in enumerate(groups):
  table=[]
  for w in W:
   if len(w)!=len(us):continue
   for d in (['FWD'] if mode=='FWD' else ['FWD','REV']):
    m=partial(w if d=='FWD' else w[::-1],us)
    if m is not None:table.append((w,d,m))
  if not table:return {'status':'UNSAT','reason':'empty_candidate_table'}
  x=z3.Int('w'+str(i));choices.append(x);tables.append(table);solver.add(x>=0,x<len(table))
  for j,(_,_,m) in enumerate(table):solver.add(z3.Implies(x==j,z3.And([f[c]==ui[u] for c,u in m.items()])))
 outcome=solver.check()
 if outcome==z3.unknown:return {'status':'UNKNOWN','reason':solver.reason_unknown()}
 if outcome==z3.unsat:return {'status':'UNSAT','reason':'complete_finite_choice_SMT'}
 m=solver.model();selected=[t[m.eval(x).as_long()] for t,x in zip(tables,choices)]
 r={'status':'SAT','words':[x[0] for x in selected],'directions':[x[1] for x in selected],
    'key':{c:signs[m.eval(v,model_completion=True).as_long()] for c,v in f.items()}}
 certificate(r,groups,W,signs,mode);return r
def controls():
 count=0
 for W in [['a','b','ab'],['aa','ab','ba'],['ab','ac']]:
  alpha=sorted(set(''.join(W)))
  for mode in ['FWD','BIDIR']:
   for flat in itertools.product('xy',repeat=4):
    gs=[list(flat[:2]),list(flat[2:])];expected=False
    for values in itertools.product('xy',repeat=len(alpha)):
     k=dict(zip(alpha,values))
     if all(any([k[c] for c in text]==g for w in W for text in ([w] if mode=='FWD' else [w,w[::-1]])) for g in gs):expected=True;break
    r=solve(gs,W,list('xy'),mode,5);assert r['status']==('SAT' if expected else 'UNSAT');count+=1
 assert partial('ab',['x','x']) is not None and partial('aa',['x','y']) is None
 assert solve([list('xy'),list('zx')],['ab','ac'],list('xyz'),'FWD',5)['status']=='UNSAT'
 assert keep(['e','i','e']) and not keep(['e','e']) and not keep(['d','y']) and keep(['d','y','a'])
 return {'status':'PASS','exhaustive_function_orientation_cases':count,'merge_not_split':True,'fixed_predicate':True}
def native_packet(s):
 p=read(ROOT/s['native_path']);rows=[r for l in p['source_unit']['lines'] for r in l['groups']];units=[];signs=sorted(s['signs'],key=lambda u:(-len(u),u))
 assert len(rows)==77 and rows==p['original_groups']
 for row in rows:
  text=row[2];i=0;us=[]
  while i<len(text):
   u=next((u for u in signs if text.startswith(u,i)),None);assert u is not None;us.append(u);i+=len(u)
  units.append(us)
 assert units==p['original_units'];ids=[i for i,u in enumerate(units) if keep(u)];assert len(ids)==46
 old=read(ROOT/s['old_subset_result'])
 assert old['original_groups']==rows and old['original_units']==units
 assert old['positions_zero_based']==ids
 assert old['freed_positions']==[i for i in range(77) if i not in ids]
 assert old['groups']==[units[i] for i in ids]
 return rows,units,ids
def gate(s):
 old=read(ROOT/s['old_control']);assert old['status']=='PASS_EXACT_UNIQUE'
 ids=[i for i,g in enumerate(old['encoded_groups']) if keep(g)];gs=[old['encoded_groups'][i] for i in ids];ws=[old['source_words'][i] for i in ids]
 active=set(''.join(ws));pairs=old['active_collision_pairs']
 if len(set(map(tuple,gs)))<2 or not all(set(pair)<=active for pair in pairs):save('INDEPENDENT_CONTROL.json',{'status':'STOP','reason':'DOMAIN_ABSENT'});return
 W=vocab(s)['deot'];certificate({'key':old['planted_key'],'words':ws,'directions':['FWD']*len(gs)},gs,W,s['signs'],'FWD')
 r=solve(gs,W,s['signs'],'FWD',s['seconds_per_case']);status='PASS' if r['status']=='SAT' else 'STOP'
 save('INDEPENDENT_CONTROL.json',{'status':status,'result':r,'selected_indices':ids,'groups':gs,'source_words':ws,'active_collision_pairs':pairs,'controls':controls()})
 print(json.dumps({'independent_gate':status,'solver_status':r['status']}))
def worker(job):
 n,m,gs,W,s=job;return {'source':n,'mode':m,'result':solve(gs,W,s['signs'],m,s['seconds_per_case'])}
def native(s):
 assert read(A/'GATE_VALIDATION.json')['status']=='PASS' and read(A/'INDEPENDENT_CONTROL.json')['status']=='PASS'
 rows,us,ids=native_packet(s);gs=[us[i] for i in ids];W=vocab(s)
 jobs=[(n,m,gs,W[n],s) for n in s['source_names'] for m in s['modes']]
 with concurrent.futures.ProcessPoolExecutor(max_workers=s['workers']) as pool:cases=list(pool.map(worker,jobs))
 save('INDEPENDENT_RESULT.json',{'cases':cases,'positions_zero_based':ids})
 print(json.dumps({'independent_statuses':[x['result']['status'] for x in cases]}))
def validate(s):
 own=read(A/'INDEPENDENT_CONTROL.json');primary=read(A/'CONTROL_SUBSET.json');W=vocab(s)
 def cert(r,gs,name,mode):
  if r['status']=='SAT':certificate({'key':r['key'],'words':r['source_words'],'directions':r['directions']},gs,W[name],s['signs'],mode)
 if own['status']!='PASS' or primary['status']!='PASS':
  assert not (A/'RESULT.json').exists();save('VALIDATION.json',{'status':'PASS_CONTROL_STOP_ACCOUNTING','native_authorized':False});return
 assert own['selected_indices']==primary['selected_indices'] and own['groups']==primary['groups'] and own['source_words']==primary['source_words']
 cert(primary['result'],own['groups'],'deot','FWD')
 rows,us,ids=native_packet(s);p=read(A/'RESULT.json');q=read(A/'INDEPENDENT_RESULT.json');gs=[us[i] for i in ids]
 assert p['original_groups']==rows and p['original_units']==us and p['positions_zero_based']==ids==q['positions_zero_based']
 assert p['freed_positions']==[i for i in range(77) if i not in ids] and p['groups']==gs
 assert p['lock_sha256']==sha(E/'LOCK.json') and p['claim_ceiling']==s['claim_ceiling']
 expected=[(n,m) for n in s['source_names'] for m in s['modes']];assert [(x['source'],x['mode']) for x in p['cases']]==[(x['source'],x['mode']) for x in q['cases']]==expected
 receipts=[]
 for a,b in zip(p['cases'],q['cases']):
  cert(a['result'],gs,a['source'],a['mode'])
  if b['result']['status']=='SAT':certificate(b['result'],gs,W[b['source']],s['signs'],b['mode'])
  statuses={a['result']['status'],b['result']['status']};assert statuses!={'SAT','UNSAT'}
  receipts.append({'source':a['source'],'mode':a['mode'],'effective':'SAT_CAPACITY_ONLY' if 'SAT' in statuses else 'UNSAT' if statuses=={'UNSAT'} else 'UNRESOLVED'})
 save('VALIDATION.json',{'status':'PASS_INDEPENDENT_CORE_AND_DUAL_RESULTS','cases':receipts,'validator_sha256':sha(Path(__file__)),'lock_sha256':sha(E/'LOCK.json'),'scope':'Necessary fixed core only; no full minim decoder, meaning or source identification.'})
 print(json.dumps({'status':'PASS_INDEPENDENT_CORE_AND_DUAL_RESULTS'}))
def main():
 p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True)
 for mode in ['controls','gate','native','validate']:g.add_argument('--'+mode,action='store_true')
 a=p.parse_args()
 if a.controls:print(json.dumps(controls()));return
 s=setup()
 if a.gate:gate(s)
 elif a.native:native(s)
 else:validate(s)
if __name__=='__main__':main()
