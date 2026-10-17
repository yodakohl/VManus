#!/usr/bin/env python3
"""Boolean finite SOURCE->unit capacity. No aligned plaintext/key is a solve input."""
from pathlib import Path
import json,gzip,hashlib,importlib.util,itertools,time,argparse,concurrent.futures
import z3
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2];A=E/'artifacts'
def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,obj):
 p=A/name;assert not p.exists(),'Refuse result overwrite: '+name;p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def setup():
 s=read(E/'src/SPEC.json')
 for p,h in s['input_sha256'].items():assert sha(ROOT/p)==h,p
 lock=read(E/'LOCK.json')
 for p,h in lock['files'].items():assert sha(ROOT/p)==h,p
 return s

def vocab(s):
 a=read(ROOT/s['source_paths']['recipes']);b=read(ROOT/s['source_paths']['deot']);c=read(ROOT/s['source_paths']['others']);out={}
 for n in s['source_names']:
  if n in ['b4','w1','bs1','gr1']:ws=[w for r in a[n] for w in r['words']]
  elif n=='deot':ws=[w for r in b['source_sections'] for w in r['words']]
  else:
   rr=c[n]['PRIMARY']['units'];assert len(rr)==8000;ws=[r['unit'] for r in rr]
  assert all(isinstance(w,str) and w for w in ws);out[n]=sorted(set(ws))
 return out

def solve(groups,words,signs,mode,caps):
 started=time.monotonic();W=sorted(set(words));alpha=sorted(set(''.join(W)));unique=sorted(set(map(tuple,groups)));tables=[]
 def expired():return time.monotonic()-started>caps['preparation_seconds']
 assert unique and mode in ['FWD','BIDIR']
 bylen={}
 for w in W:bylen.setdefault(len(w),[]).append(w)
 for g in unique:
  t={}
  for w in bylen.get(len(g),[]):
   for direction,txt in [('FWD',w)]+([('REV',w[::-1])] if mode=='BIDIR' else []):
    d={}
    for c,u in zip(txt,g):
     if c in d and d[c]!=u:break
     d[c]=u
    else:t.setdefault(tuple(sorted(d.items())),(w,direction))
   if expired():return {'status':'UNKNOWN','reason':'PREPARATION_CAP_TABLES'}
  if not t:return {'status':'UNSAT','reason':'EMPTY_COMPLETE_CANDIDATE_TABLE','units':list(g),'preparation_seconds':time.monotonic()-started}
  tables.append(t)
 solver=z3.SolverFor('QF_FD');solver.set(timeout=int(caps['solver_seconds']*1000))
 binding={(c,u):z3.Bool(f'k{ci}_{ui}') for ci,c in enumerate(alpha) for ui,u in enumerate(signs)}
 for c in alpha:
  lits=[binding[c,u] for u in signs];solver.add(z3.Or(lits),z3.AtMost(*lits,1))
 for table in tables:
  solver.add(z3.Or([z3.And([binding[c,u] for c,u in row]) for row in table]))
  if expired():return {'status':'UNKNOWN','reason':'PREPARATION_CAP_ENCODING'}
 prep=time.monotonic()-started;solve_start=time.monotonic();outcome=solver.check();elapsed=time.monotonic()-solve_start
 stats={'preparation_seconds':prep,'solve_seconds':elapsed,'distinct_groups':len(unique),'mapping_cubes':sum(map(len,tables)),'source_characters':len(alpha),'unit_values':len(signs)}
 if outcome==z3.unknown:return {'status':'UNKNOWN','reason':solver.reason_unknown(),'stats':stats}
 if outcome==z3.unsat:return {'status':'UNSAT','reason':'EXHAUSTIVE_BOOLEAN_MAPPING_CUBES','stats':stats}
 m=solver.model();key={}
 for c in alpha:
  us=[u for u in signs if z3.is_true(m.eval(binding[c,u],model_completion=True))];assert len(us)==1;key[c]=us[0]
 chosen={}
 for g,t in zip(unique,tables):
  row=next(row for row in t if all(key[c]==u for c,u in row));chosen[g]=t[row]
 ws=[];ds=[]
 for g in groups:
  w,d=chosen[tuple(g)];txt=w if d=='FWD' else w[::-1];assert [key[c] for c in txt]==g;ws.append(w);ds.append(d)
 return {'status':'SAT','key':key,'words':ws,'directions':ds,'stats':stats}

def selftest():
 count=0;caps={'preparation_seconds':10,'solver_seconds':2};pool=['a','b','ab','aa']
 for mask in range(1,16):
  ws=[w for i,w in enumerate(pool) if mask>>i&1];alpha=sorted(set(''.join(ws)))
  for gs in [[['X']],[['Y']],[['X','Y']],[['X','X']],[['X'],['Y']],[['X','Y'],['Y','X']]]:
   for mode in ['FWD','BIDIR']:
    possible=any(all(any([dict(zip(alpha,vals))[c] for c in txt]==g for w in ws for txt in ([w] if mode=='FWD' else [w,w[::-1]])) for g in gs) for vals in itertools.product('XY',repeat=len(alpha)))
    r=solve(gs,ws,list('XY'),mode,caps);assert r['status']==('SAT' if possible else 'UNSAT');count+=1
 assert solve([['X','X']],['ab'],list('XY'),'FWD',caps)['status']=='SAT'
 assert solve([['X','Y']],['aa'],list('XY'),'FWD',caps)['status']=='UNSAT'
 return {'status':'PASS_SOURCE_FREE_EXHAUSTIVE_FUNCTION_CONTROLS','cases':count,'note':'Development before common lock, not native evidence.'}

def gate(s):
 old=read(ROOT/s['control_path']);subset=read(ROOT/s['control_subset_path']);assert subset['status']=='STOP'
 groups=subset['groups'];indices=subset['selected_indices'];assert len(groups)==32 and indices==list(range(32));assert groups==old['encoded_groups']
 # The solve call receives neither the planted key nor aligned source words.
 r=solve(groups,vocab(s)['deot'],s['signs'],'FWD',s['search'])
 save('CONTROL.json',{'status':'PASS' if r['status']=='SAT' else 'STOP','result':r,'groups':groups,'selected_indices':indices,'control_sha256':sha(ROOT/s['control_path']),'lock_sha256':sha(E/'LOCK.json'),'scope':'ANY-key necessary control capacity only; original1421STOP retained.'});print(json.dumps({'gate':'PASS' if r['status']=='SAT' else 'STOP','result_status':r['status'],'stats':r.get('stats',{})}),flush=True)

def job(args):
 n,m,gs,ws,s=args;return {'source':n,'mode':m,'result':solve(gs,ws,s['signs'],m,s['search'])}
def native(s):
 assert read(A/'GATE_VALIDATION.json')['status']=='PASS';p=read(ROOT/s['core_path']);gs=p['groups'];ids=p['positions_zero_based'];assert len(gs)==len(ids)==46
 W=vocab(s);jobs=[(n,m,gs,W[n],s) for n in s['source_names'] for m in s['modes']]
 with concurrent.futures.ProcessPoolExecutor(max_workers=s['search']['workers']) as pool:cases=list(pool.map(job,jobs))
 save('RESULT.json',{'status':'BOOLEAN_FIXED_FORWARD_CORE_CASES','cases':cases,'positions_zero_based':ids,'groups':gs,'core_sha256':sha(ROOT/s['core_path']),'lock_sha256':sha(E/'LOCK.json'),'claim_ceiling':'Necessary core capacity only; no source/word meaning or actual alphabet.'});print(json.dumps({'cases':[(x['source'],x['mode'],x['result']['status']) for x in cases]}),flush=True)
def main():
 p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True)
 for x in ['selftest','gate','native']:g.add_argument('--'+x,action='store_true')
 a=p.parse_args()
 if a.selftest:print(json.dumps(selftest()));return
 s=setup()
 if a.gate:gate(s)
 else:native(s)
if __name__=='__main__':main()
