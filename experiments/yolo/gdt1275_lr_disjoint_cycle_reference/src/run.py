"""Fixed label-blind disjoint cycles; exact restricted-orbit moments."""
import collections, hashlib, itertools, json
from fractions import Fraction
from pathlib import Path
B=Path(__file__).resolve().parents[1]; R=B.parents[2]
def dump(path,obj):path.write_text(json.dumps(obj,indent=2)+'\n')
def graph(tokens):
 return [(('L',t['page'],t['locus']),('S',t['leaf'],t['stem'],t['position'])) for t in tokens]
def pack(edges,ids,priority):
 key=lambda i:(ids[i],i)
 adj=collections.defaultdict(list)
 for i,(u,v) in enumerate(edges):adj[u].append((v,i));adj[v].append((u,i))
 for u in adj:adj[u].sort(key=lambda vi:key(vi[1]))
 used=set();cycles=[]
 for anchor in sorted(range(len(edges)),key=lambda i:(i not in priority,key(i))):
  if anchor in used:continue
  u,v=edges[anchor];back={u:None};q=collections.deque([u])
  while q and v not in back:
   at=q.popleft()
   for dest,j in adj[at]:
    if j==anchor or j in used or dest in back:continue
    back[dest]=(at,j);q.append(dest)
  if v not in back:continue
  cycle=[anchor];at=v
  while at!=u:prev,j=back[at];cycle.append(j);at=prev
  cycles.append(cycle);used.update(cycle)
 return cycles

def moments(labels,cycles,pairs):
 owner={};active=[]
 for ci,cy in enumerate(cycles):
  if all(labels[cy[k]]!=labels[cy[(k+1)%len(cy)]] for k in range(len(cy))):
   active.append(ci)
   for i in cy:owner[i]=ci
 coeff=collections.Counter()
 for a,b in pairs:
  monomial=set()
  for i in (a,b):
   if i in owner:
    c=owner[i]
    if c in monomial:monomial.remove(c)
    else:monomial.add(c)
  coeff[tuple(sorted(monomial))]+=labels[a]*labels[b]
 obs=sum(labels[a]*labels[b] for a,b in pairs)
 return obs,coeff[()],sum(v*v for k,v in coeff.items() if k),active,coeff

def controls():
 graphs=[[(0,10),(0,10)],[(0,10),(0,11),(1,10),(1,11)],[(0,10),(0,10),(0,11),(0,11)],[(0,10),(0,11),(1,10),(1,11),(1,12),(2,12),(2,11)],[(0,10),(0,11),(1,11)]]
 n=0
 for edges in graphs:
  cycles=pack(edges,[str(i) for i in range(len(edges))],set())
  for labels in itertools.product([-1,1],repeat=len(edges)):
   pairs=[(i,i+1) for i in range(len(edges)-1)]
   obs,mean,var,active,_=moments(labels,cycles,pairs)
   values=[]
   def margin(y):
    c=collections.Counter()
    for (u,v),s in zip(edges,y):c[u]+=s;c[v]+=s
    return c
   for bits in itertools.product([0,1],repeat=len(active)):
    y=list(labels)
    for ci,bit in zip(active,bits):
     if bit:
      for i in cycles[ci]:y[i]*=-1
    assert margin(y)==margin(labels)
    values.append(sum(y[a]*y[b] for a,b in pairs))
   assert Fraction(sum(values),len(values))==mean
   assert sum(Fraction((v-mean)**2,len(values)) for v in values)==var
   n+=1
 # Explicit cancellation: two terms share a spin and opposite coefficients.
 assert moments([1,-1,1],[[0,1]],[(0,2),(1,2)])[2]==0
 return n

def main():
 lock=json.loads((B/'src/REGISTRATION_LOCK.json').read_text())
 for p,h in lock['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 src=R/'experiments/yolo/gdt1260_lr_line_margin_capacity/artifacts'
 tokens=json.loads((src/'TOKENS.json').read_text());pairs=json.loads((src/'PAIRS.json').read_text())
 nom=set(map(tuple,json.loads((R/'experiments/yolo/gdt915_terminal_lr_phrase_transfer/artifacts/CANDIDATES.json').read_text())));assert len(nom)==22
 result={'readers':{},'claim_ceiling':'Exact restricted orbit only, fixed old nominees; no full-fibre inference, significance, independent holdout or meaning.'};details={}
 for reader in ['ZL3b','IT2a','RF1b']:
  ts=tokens[reader];ps=pairs[reader];ns=[p for p in ps if tuple(p['stems']) in nom]
  assert all(not t['page'].startswith('f84') and t['page']!='f116v' for t in ts)
  cycles=pack(graph(ts),[t['source_id'] for t in ts],{p[k] for p in ns for k in ['a','b']})
  labels=[1 if t['ending']=='l' else -1 for t in ts]
  den=collections.Counter(p['leaf'] for p in ps);leaves=[]
  _,_,_,active,_=moments(labels,cycles,[])
  for leaf,d in sorted(den.items()):
   sub=[(p['a'],p['b']) for p in ns if p['leaf']==leaf]
   obs,mean,var,_,coeff=moments(labels,cycles,sub)
   leaves.append({'leaf':leaf,'all_pairs':d,'nominated_pairs':len(sub),'observed_numerator':obs,'expected_numerator':mean,'variance_numerator':var,'residual':str(Fraction(obs-mean,d)),'nonzero_terms':[{'cycles':list(k),'coefficient':v} for k,v in sorted(coeff.items()) if v]})
  N=len(leaves);observed=sum(Fraction(x['observed_numerator'],x['all_pairs']) for x in leaves)/N;expected=sum(Fraction(x['expected_numerator'],x['all_pairs']) for x in leaves)/N
  variance=sum(Fraction(x['variance_numerator'],x['all_pairs']**2) for x in leaves)/N**2
  res=observed-expected;loo=min((res*N-Fraction(x['residual']))/(N-1) for x in leaves)
  mobile=[x['leaf'] for x in leaves if x['variance_numerator']>0]
  status='CAPACITY_STOP' if len(mobile)<5 else ('ROBUST_POSITIVE_RESIDUAL' if res>0 and loo>0 else 'NONCONFIRMING_OR_FRAGILE')
  result['readers'][reader]={'status':status,'tokens':len(ts),'all_pairs':len(ps),'nominated_pairs':len(ns),'eligible_leaves':N,'selected_cycles':len(cycles),'active_cycles':len(active),'score_variable_leaves':mobile,'observed':str(observed),'expected':str(expected),'variance':str(variance),'residual':str(res),'minimum_leave_one_out_residual':str(loo),'observed_decimal':float(observed),'expected_decimal':float(expected),'residual_decimal':float(res)}
  details[reader]={'cycles':cycles,'active_cycle_indices':active,'leaves':leaves}
 result['status']=result['readers']['ZL3b']['status'];result['synthetic_controls']=controls()
 dump(B/'artifacts/DETAILS.json',details);dump(B/'artifacts/RESULT.json',result);print(json.dumps(result,indent=2))
if __name__=='__main__':
 import sys
 if '--controls' in sys.argv:print(controls())
 else:main()
