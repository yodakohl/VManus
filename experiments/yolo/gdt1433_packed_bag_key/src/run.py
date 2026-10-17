#!/usr/bin/env python3
"""One compact no-carry bitvector representation of the fixed bag-key contract."""
import argparse,hashlib,itertools,json,random,time
from collections import Counter,defaultdict
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
 assert s['mode']=='PACKED_BAG_KEY'
 receipt=read(E/'REGISTRATION_PUBLICATION.json')
 assert receipt['status']=='PUSH_VERIFIED' and receipt['lock_sha256']==sha(E/'LOCK.json')
 return s

def solve(groups,W,signs,limits):
 start=time.monotonic();assert signs and len(set(signs))==len(signs)
 alphabet=sorted(set(''.join(W)));largest=max([0]+[len(w) for w in W]+[len(g) for g in groups])
 digit_bits=max(1,largest.bit_length());base=1<<digit_bits;width=digit_bits*len(signs)
 assert largest<base
 power=[1<<(i*digit_bits) for i in range(len(signs))]
 k={c:z3.BitVec('packed_%d'%i,width) for i,c in enumerate(alphabet)}
 solver=z3.SolverFor('QF_BV');solver.set(timeout=int(limits['solver_seconds']*1000),random_seed=1433)
 for c in alphabet:solver.add(z3.Or([k[c]==z3.BitVecVal(v,width) for v in power]))
 bylength=defaultdict(dict)
 for w in W:
  profile=tuple(sorted(Counter(w).items()))
  if profile not in bylength[len(w)]:
   total=z3.BitVecVal(0,width)
   for c,n in profile:total=total+z3.BitVecVal(n,width)*k[c]
   bylength[len(w)][profile]=total
 distinct=list(dict.fromkeys(tuple(sorted(Counter(g).items())) for g in groups));counts=[]
 for target in distinct:
  if time.monotonic()-start>limits['preparation_seconds']:
   return {'status':'UNKNOWN','reason':'PREPARATION_TIME_CAP','prepared_bags':len(counts),'preparation_seconds':time.monotonic()-start}
  val=sum(n*power[signs.index(sign)] for sign,n in target);assert val<1<<width
  terms=list(bylength[sum(n for _,n in target)].values())
  solver.add(z3.Or([term==z3.BitVecVal(val,width) for term in terms]));counts.append(len(terms))
 prep=time.monotonic()-start
 stats={'source_letters':len(alphabet),'source_forms':len(W),'source_multisets':sum(len(v) for v in bylength.values()),'target_groups':len(groups),'target_multisets':len(distinct),'case_counts':counts,'max_word_length':largest,'base':base,'digit_bits':digit_bits,'bitvector_width':width,'preparation_seconds':prep,'backend':'z3-'+z3.get_version_string(),'encoding':'NONCARRY_BITVECTOR_WORD_SUM'}
 if prep>limits['preparation_seconds']:return {'status':'UNKNOWN','reason':'PREPARATION_TIME_CAP','stats':stats}
 then=time.monotonic();answer=solver.check();stats['solver_seconds']=time.monotonic()-then
 if answer==z3.unknown:return {'status':'UNKNOWN','reason':solver.reason_unknown(),'stats':stats}
 if answer==z3.unsat:return {'status':'UNSAT','reason':'EXHAUSTIVE_PACKED_BITVECTOR_CONSTRAINTS','stats':stats}
 model=solver.model();key={c:signs[power.index(model.eval(k[c],model_completion=True).as_long())] for c in alphabet}
 index=defaultdict(list)
 for w in sorted(W):index[tuple(sorted(Counter(key[c] for c in w).items()))].append(w)
 words=[index[tuple(sorted(Counter(g).items()))][0] for g in groups]
 for w,g in zip(words,groups):assert Counter(key[c] for c in w)==Counter(g)
 return {'status':'SAT','reason':'DIRECTLY_VERIFIED_ANY_BAG_KEY','key':key,'words':words,'stats':stats,'limits':'No preferred or unique word; no within-word order rule or meaning selected.'}

def brute(groups,W,signs):
 alpha=sorted(set(''.join(W)))
 for vals in itertools.product(signs,repeat=len(alpha)):
  key=dict(zip(alpha,vals));available={tuple(sorted(Counter(key[c] for c in w).items())) for w in W}
  if all(tuple(sorted(Counter(g).items())) in available for g in groups):return True
 return False

def fixtures():
 cases=[(['ab'],[['y','x']],list('xy')),(['aa'],[['x','y']],list('xy')),(['a','aa'],[['x'],['y','y']],list('xy')),(['ab','aa'],[['x','y'],['x','x']],list('xy')),(['aba'],[['x','x','x']],list('xy')),(['a'],[['x','x']],list('xy')),([''],[[]],list('xy')),([],[["x"]],list('xy')),(['a'],[['z']],list('xyz')),(['aaaaaaa'],[['z']*7],list('xyz')),(['aa'],[['y']],list('xy')),(['ab'],[['x','x']],list('xy'))]
 cases.extend([(['a'*n],[['u21']*n],['u'+str(i) for i in range(22)]) for n in (7,33)])
 rng=random.Random(1433);universe=['a','b','c','aa','ab','ba','bb','aba','aab','bab','abc','aac'];targets=[['x'],['y'],['z'],['x','x'],['x','y'],['y','x'],['y','y'],['x','y','x'],['x','y','z']]
 for _ in range(36):cases.append((sorted(rng.sample(universe,rng.randint(1,4))),[list(rng.choice(targets)) for _ in range(rng.randint(1,3))],list('xyz')))
 results=[]
 for W,groups,signs in cases:
  expected=brute(groups,W,signs);r=solve(groups,W,signs,{'preparation_seconds':20,'solver_seconds':20})
  assert r['status']==('SAT' if expected else 'UNSAT'),(W,groups,r)
  results.append({'W':W,'groups':groups,'signs':signs,'expected_sat':expected,'status':r['status']})
 return {'status':'PASS','fixture_count':len(results),'cases':results,'scope':'Source-free exhaustive tiny functions, mergers, absent lengths, empty cases and high-bin no-carry/overflow boundaries; no actual control/native solve.'}

def main():
 p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True)
 for v in ['fixtures','gate','native']:g.add_argument('--'+v,action='store_true')
 args=p.parse_args()
 if args.fixtures:print(json.dumps(fixtures()));return
 s=setup();source=read(ROOT/s['source_projection']);W=source['words'];assert len(W)==2133 and len(source['alphabet'])==23
 if args.native:assert read(A/'GATE_VALIDATION.json')['status']=='PASS','No native after control stop'
 ip=ROOT/s['control_input' if args.gate else 'native_input'];groups=read(ip)['groups'];assert len(groups)==(32 if args.gate else 59)
 name='CONTROL_PRIMARY.json' if args.gate else 'RESULT.json';assert not (A/name).exists(),'No repeated actual search'
 started=time.time();then=time.monotonic();r=solve(groups,W,s['signs'],s['primary_search']);elapsed=time.monotonic()-then
 save(name,{'status':r['status'],'result':r,'elapsed_seconds':elapsed,'started_epoch':started,'input_sha256':sha(ip),'source_projection_sha256':sha(ROOT/s['source_projection']),'lock_sha256':sha(E/'LOCK.json')})
 print(json.dumps({'phase':'gate' if args.gate else 'native','status':r['status'],'elapsed_seconds':elapsed,'stats':r.get('stats'),'reason':r.get('reason')}),flush=True)
if __name__=='__main__':main()
