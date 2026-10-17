#!/usr/bin/env python3
"""Finite integer-key / Parikh-vector necessary capacity; no plaintext ordering."""
import argparse,hashlib,itertools,json,random,time
from collections import Counter
from pathlib import Path
import z3
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2];A=E/'artifacts'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,obj):
 p=A/name;assert not p.exists(),'Refuse overwrite '+name
 p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def setup():
 s=read(E/'src/SPEC.json')
 for p,h in read(E/'LOCK.json')['files'].items():assert sha(ROOT/p)==h,p
 for p,h in s['predecessor_sha256'].items():assert sha(ROOT/p)==h,p
 assert s['mode']=='ARBITRARY_WITHIN_WORD_PERMUTATION'
 return s

def solve(groups,W,signs,limits):
 start=time.monotonic();alphabet=sorted(set(''.join(W)));k={c:z3.Int('K'+str(i)) for i,c in enumerate(alphabet)}
 solver=z3.Solver();solver.set(timeout=limits['solver_seconds']*1000,random_seed=1431)
 solver.add(*[z3.And(v>=0,v<len(signs)) for v in k.values()])
 bags={};bylength={}
 for w in W:
  p=tuple(sorted(Counter(w).items()));bags.setdefault(p,[]).append(w)
 for p,ws in bags.items():bylength.setdefault(sum(n for _,n in p),[]).append(p)
 hist={}
 def count(p,i):
  key=(p,i)
  if key not in hist:hist[key]=z3.Sum([z3.If(k[c]==i,n,0) for c,n in p])
  return hist[key]
 distinct=list(dict.fromkeys(tuple(sorted(Counter(g).items())) for g in groups));casecounts=[]
 for target in distinct:
  if time.monotonic()-start>limits['preparation_seconds']:
   return {'status':'UNKNOWN','reason':'PREPARATION_TIME_CAP','prepared_bags':len(casecounts)}
  tc=dict(target);cases=[]
  for p in bylength.get(sum(tc.values()),[]):
   # Necessary domain reductions only: a source letter cannot exceed its output bin.
   if len(p)<len(tc) or max(n for _,n in p)>max(tc.values()):continue
   clauses=[count(p,i)==tc.get(sign,0) for i,sign in enumerate(signs)]
   cases.append(z3.And(*clauses))
  solver.add(z3.Or(*cases));casecounts.append(len(cases))
 prep=time.monotonic()-start
 if prep>limits['preparation_seconds']:return {'status':'UNKNOWN','reason':'PREPARATION_TIME_CAP','preparation_seconds':prep}
 solve_start=time.monotonic();answer=solver.check();elapsed=time.monotonic()-solve_start
 stats={'source_letters':len(alphabet),'source_forms':len(W),'source_multisets':len(bags),'target_groups':len(groups),'target_multisets':len(distinct),'case_counts':casecounts,'preparation_seconds':prep,'solver_seconds':elapsed,'backend':'z3-'+z3.get_version_string(),'encoding':'INTEGER_KEY_WEIGHTED_COUNT_DISJUNCTIONS'}
 if answer==z3.unknown:return {'status':'UNKNOWN','reason':solver.reason_unknown(),'stats':stats}
 if answer==z3.unsat:return {'status':'UNSAT','reason':'EXHAUSTIVE_INTEGER_PARIKH_CONSTRAINTS','stats':stats}
 m=solver.model();key={c:signs[m.eval(k[c],model_completion=True).as_long()] for c in alphabet};words=[]
 for g in groups:
  want=Counter(g);matches=[w for w in W if Counter(key[c] for c in w)==want];assert matches
  words.append(matches[0])
 return {'status':'SAT','reason':'VERIFIED_FIRST_ANY_KEY_BAG_CERTIFICATE','key':key,'words':words,'stats':stats,'limits':'No uniqueness or preferred plaintext. Words are arbitrary certificate witnesses, not readings.'}

def oracle(groups,W,signs):
 alpha=sorted(set(''.join(W)))
 for values in itertools.product(signs,repeat=len(alpha)):
  key=dict(zip(alpha,values));enc={tuple(sorted(Counter(key[c] for c in w).items())) for w in W}
  if all(tuple(sorted(Counter(g).items())) in enc for g in groups):return True
 return False

def fixtures():
 cases=[(['ab'],[['y','x']]),(['aa'],[['x','y']]),(['a','aa'],[['x'],['y','y']]),(['ab','aa'],[['x','y'],['x','x']]),(['aba'],[['x','x','x']]),(['a'],[['x','x']])]
 rng=random.Random(1431);universe=['a','b','aa','ab','ba','bb','aba','aab','bab'];targets=[['x'],['y'],['x','x'],['x','y'],['y','x'],['y','y'],['x','y','x']]
 for _ in range(26):cases.append((sorted(rng.sample(universe,rng.randint(1,4))),[list(rng.choice(targets)) for _ in range(rng.randint(1,3))]))
 results=[]
 for W,groups in cases:
  expected=oracle(groups,W,['x','y']);r=solve(groups,W,['x','y'],{'preparation_seconds':20,'solver_seconds':20});assert r['status']==('SAT' if expected else 'UNSAT'),(W,groups,r)
  results.append({'W':W,'groups':groups,'expected_sat':expected,'status':r['status']})
 return {'status':'PASS','fixture_count':len(results),'cases':results,'scope':'Source-free tiny complete key enumeration. No native/source-control solve.'}

def main():
 p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True)
 for v in ['fixtures','gate','native']:g.add_argument('--'+v,action='store_true')
 args=p.parse_args()
 if args.fixtures:print(json.dumps(fixtures()));return
 s=setup();source=read(ROOT/s['source_projection']);W=source['words'];assert len(W)==2133 and len(source['alphabet'])==23
 kind='gate' if args.gate else 'native';ip=ROOT/s['control_input' if args.gate else 'native_input'];inp=read(ip);groups=inp['groups']
 if args.native:
  assert read(A/'GATE_VALIDATION.json')['status']=='PASS','Control stop; no native solve'
 assert len(groups)==(32 if args.gate else 59)
 start=time.monotonic();r=solve(groups,W,s['signs'],s['primary_search']);elapsed=time.monotonic()-start
 save('CONTROL_PRIMARY.json' if args.gate else 'RESULT.json',{'status':r['status'],'result':r,'elapsed_seconds':elapsed,'input_sha256':sha(ip),'source_projection_sha256':sha(ROOT/s['source_projection']),'lock_sha256':sha(E/'LOCK.json')})
 print(json.dumps({'phase':kind,'status':r['status'],'elapsed_seconds':elapsed,'stats':r.get('stats'),'reason':r.get('reason')}),flush=True)
if __name__=='__main__':main()
