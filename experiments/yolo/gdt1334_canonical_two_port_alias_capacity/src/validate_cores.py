"""Independent brute checks of post-result explanatory n/q certificates."""
from pathlib import Path
import gzip,itertools,json,hashlib
B=Path(__file__).resolve().parents[1];R=B.parents[2]
U=sorted('a o e i n d q y s r l m k t p f ch sh ckh cth cph cfh'.split())
def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def has_model(clauses):
 variables=sorted({abs(l) for c in clauses for l in c})
 for values in itertools.product((False,True),repeat=len(variables)):
  assignment=dict(zip(variables,values))
  if all(any(assignment[abs(l)]==(l>0) for l in c) for c in clauses):return True
 return False
def main():
 result=read(B/'artifacts/NQ_UNSAT_CORES.json');parent=read(B/'artifacts/PAIR_RESULTS.json.gz');data=read(R/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz');assert hashlib.sha256((B/'artifacts/PAIR_RESULTS.json.gz').read_bytes()).hexdigest()==result['source_sha256'];count=0;nw=0
 for ed,cores in result['readers'].items():
  rows={r['id']:r for r in data[ed]};pr=next(r for r in parent[ed] if r['pair']==['n','q']);assert len(cores)==12
  for core,case in zip(cores,pr['port_cases']):
   assert core['pair_ports']==case['pair_ports'];clauses=core['clauses'];assert all(c in case['clauses'] for c in clauses);assert not has_model(clauses)
   for j in range(len(clauses)):assert has_model(clauses[:j]+clauses[j+1:])
   assert len(core['original_run_witnesses'])==len(clauses);ports=dict(zip(('n','q'),core['pair_ports']))
   for c,e in zip(clauses,core['original_run_witnesses']):
    row=e['row'];assert rows[row['id']]==row;w=row['units'];a,b=e['run_start'],e['run_end'];assert 0<=a<b<=len(w) and all(u in ports for u in w[a:b]);assert a==0 or w[a-1] not in ports;assert b==len(w) or w[b] not in ports;lv,rv=e['outside_values'];assert (lv is None)==(a==0) and (rv is None)==(b==len(w));allpaths=[]
    for v in itertools.product(('n','q'),repeat=b-a):
     codes=[ports[u] for u in v];cost=sum(x%2!=y//2 for x,y in zip(codes,codes[1:]));cost+=0 if lv is None else lv!=codes[0]//2;cost+=0 if rv is None else codes[-1]%2!=rv;allpaths.append((cost,tuple(codes),v))
    best=min(allpaths)[2];assert list(best)==e['canonical_run'] and tuple(w[a:b])!=best;expected=[]
    if a:
     j=2*U.index(w[a-1])+2;expected.append(j if lv==0 else -j)
    if b<len(w):
     j=2*U.index(w[b])+1;expected.append(j if rv==0 else -j)
    assert sorted(expected)==c;nw+=1
   count+=1
 out={'status':'PASS','all_nq_port_branches':count,'original_run_certificates':nw,'method':'Brute truth tables prove each clause subset UNSAT and deletion-minimal; brute2^run renderings verify every original-row forbidden boundary certificate. No optimizer or main solver imported.'};(B/'artifacts/VALIDATION_CORES.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
