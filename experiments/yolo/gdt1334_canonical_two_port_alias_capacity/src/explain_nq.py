"""Post-result explanatory certificate, not candidate selection or a new test.
Select n/q (a surviving local-frame pair in all readers), all12port assignments.
Use only already validated clauses. Fixed lexicographic deletion gives an
inclusion-minimal UNSAT subset; it is NOT minimum token-error radius.
"""
from pathlib import Path
import gzip,hashlib,json
import z3
from validate import canonical
B=Path(__file__).resolve().parents[1];R=B.parents[2]
U=sorted('a o e i n d q y s r l m k t p f ch sh ckh cth cph cfh'.split())
def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def unsat(clauses):
 vs=[z3.Bool('v'+str(i)) for i in range(44)];s=z3.Solver()
 for c in clauses:s.add(z3.Or([vs[abs(l)-1] if l>0 else z3.Not(vs[abs(l)-1]) for l in c]))
 return s.check()==z3.unsat
def origins(rows,px,py):
 out={};pair=(U.index('n'),U.index('q'));ports={pair[0]:px,pair[1]:py}
 for row in sorted(rows,key=lambda r:r['id']):
  w=[U.index(u) for u in row['units']];i=0
  while i<len(w):
   if w[i] not in pair:i+=1;continue
   j=i+1
   while j<len(w) and w[j] in pair:j+=1
   left=w[i-1] if i else None;right=w[j] if j<len(w) else None
   for lv in ([None] if left is None else [0,1]):
    for rv in ([None] if right is None else [0,1]):
     plan=canonical([pair]*(j-i),ports,lv,rv)
     if tuple(w[i:j])==plan:continue
     clause=[]
     if left is not None:
      v=2*left+2;clause.append(v if lv==0 else -v)
     if right is not None:
      v=2*right+1;clause.append(v if rv==0 else -v)
     out.setdefault(tuple(sorted(clause)),{'row':row,'run_start':i,'run_end':j,'outside_values':[lv,rv],'canonical_run':[U[k] for k in plan]})
   i=j
 return out

def main():
 data=read(B/'artifacts/PAIR_RESULTS.json.gz');groups=read(R/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz');out={}
 for ed,rs in sorted(data.items()):
  r=next(r for r in rs if r['pair']==['n','q']);assert r['status']=='ALL_PORTS_UNSAT';out[ed]=[]
  for case in r['port_cases']:
   core=case['clauses'].copy();assert unsat(core)
   for c in case['clauses']:
    candidate=[x for x in core if x!=c]
    if unsat(candidate):core=candidate
   assert unsat(core) and all(not unsat([x for x in core if x!=c]) for c in core)
   origin=origins(groups[ed],*case['pair_ports']);assert all(tuple(c) in origin for c in core)
   out[ed].append({'pair_ports':case['pair_ports'],'clauses':core,'original_run_witnesses':[origin[tuple(c)] for c in core],'clause_descriptions':[[('' if l>0 else 'NOT ')+U[(abs(l)-1)//2]+('.entry' if (abs(l)-1)%2==0 else '.exit') for l in c] for c in core]})
 result={'status':'POSTRESULT_VALIDATED_CLAUSE_SUBSETS','source_sha256':hashlib.sha256((B/'artifacts/PAIR_RESULTS.json.gz').read_bytes()).hexdigest(),'scope':'All12n/qport branches per reader, selected after main result; inclusion-minimal clause sets only, not token-error minima or new native evidence. Parent clauses/source/run definitions independently validated.','readers':out};(B/'artifacts/NQ_UNSAT_CORES.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
