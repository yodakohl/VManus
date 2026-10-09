"""Independent reverse-distance packing and pairwise covariance validation."""
import collections,hashlib,json
from fractions import Fraction
from pathlib import Path
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def main():
 lock=json.loads((B/'src/REGISTRATION_LOCK.json').read_text())
 for p,h in lock['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 src=R/'experiments/yolo/gdt1260_lr_line_margin_capacity/artifacts'
 tokens=json.loads((src/'TOKENS.json').read_text());pairs=json.loads((src/'PAIRS.json').read_text())
 nom=set(map(tuple,json.loads((R/'experiments/yolo/gdt915_terminal_lr_phrase_transfer/artifacts/CANDIDATES.json').read_text())))
 result=json.loads((B/'artifacts/RESULT.json').read_text());details=json.loads((B/'artifacts/DETAILS.json').read_text());checks={}
 for reader,ts in tokens.items():
  ps=pairs[reader];np=[p for p in ps if tuple(p['stems']) in nom];priority={p[k] for p in np for k in ('a','b')}
  edges=[(('line',t['page'],t['locus']),('cell',t['leaf'],t['stem'],t['position'])) for t in ts]
  ids=[t['source_id'] for t in ts];assert len(ids)==len(set(ids));assert all(not t['page'].startswith('f84') and t['page']!='f116v' for t in ts)
  assert all({ts[i]['leaf'] for i in [p['a'],p['b']]}=={p['leaf']} and p['stems']==[ts[i]['stem'] for i in [p['a'],p['b']]] for p in ps)
  adj=collections.defaultdict(list)
  for i,(u,v) in enumerate(edges):adj[u].append((v,i));adj[v].append((u,i))
  removed=set();expected_cycles=[]
  for a in sorted(range(len(ts)),key=lambda i:(i not in priority,ids[i],i)):
   if a in removed:continue
   start,end=edges[a];distance={end:0};queue=collections.deque([end])
   while queue:
    at=queue.popleft()
    for nxt,j in adj[at]:
     if j==a or j in removed or nxt in distance:continue
     distance[nxt]=distance[at]+1;queue.append(nxt)
   if start not in distance:continue
   at=start;path=[]
   while at!=end:
    candidates=[(ids[j],j,nxt) for nxt,j in adj[at] if j!=a and j not in removed and distance.get(nxt)==distance[at]-1]
    _,j,at=min(candidates);path.append(j)
   cy=[a]+path[::-1];assert len(cy)==len(set(cy));expected_cycles.append(cy);removed.update(cy)
  detail=details[reader];assert detail['cycles']==expected_cycles
  y=[1 if t['ending']=='l' else -1 for t in ts];owner={};active=[]
  def margins(labels):
   c=collections.Counter()
   for edge,s in zip(edges,labels):
    for vertex in edge:c[vertex]+=s
   return c
  base=margins(y);allflipped=y[:]
  for k,cy in enumerate(expected_cycles):
   if any(y[cy[j]]==y[cy[(j+1)%len(cy)]] for j in range(len(cy))):continue
   active.append(k);z=y[:];assert len({ts[j]['leaf'] for j in cy})==1
   for j in cy:owner[j]=k;z[j]*=-1;allflipped[j]*=-1
   assert margins(z)==base
  assert margins(allflipped)==base and active==detail['active_cycle_indices']
  obs_values=[];mu_values=[];var_values=[];mobile=[]
  for row in detail['leaves']:
   leaf=row['leaf'];d=sum(p['leaf']==leaf for p in ps);assert d==row['all_pairs']
   sub=[p for p in np if p['leaf']==leaf];terms=[]
   for p in sub:
    a,b=p['a'],p['b'];mask=frozenset([owner[a]]) if a in owner else frozenset()
    if b in owner:mask=mask.symmetric_difference([owner[b]])
    terms.append((y[a]*y[b],mask))
   obs=sum(s for s,m in terms);mu=sum(s for s,m in terms if not m)
   second=sum(s*t for s,m in terms for t,n in terms if m==n);var=second-mu*mu
   assert (obs,mu,var,len(sub))==(row['observed_numerator'],row['expected_numerator'],row['variance_numerator'],row['nominated_pairs'])
   actual=collections.Counter()
   for s,m in terms:actual[tuple(sorted(m))]+=s
   assert row['nonzero_terms']==[{'cycles':list(k),'coefficient':v} for k,v in sorted(actual.items()) if v]
   assert Fraction(row['residual'])==Fraction(obs-mu,d)
   obs_values.append(Fraction(obs,d));mu_values.append(Fraction(mu,d));var_values.append(Fraction(var,d*d))
   if var:mobile.append(leaf)
  assert sorted(r['leaf'] for r in detail['leaves'])==sorted({p['leaf'] for p in ps})
  N=len(obs_values);observed=sum(obs_values)/N;mean=sum(mu_values)/N;variance=sum(var_values)/N**2;delta=observed-mean
  loo=min((N*delta-(a-b))/(N-1) for a,b in zip(obs_values,mu_values))
  out=result['readers'][reader]
  for key,val in [('observed',observed),('expected',mean),('variance',variance),('residual',delta),('minimum_leave_one_out_residual',loo)]:assert Fraction(out[key])==val,key
  assert out['score_variable_leaves']==mobile
  assert (out['tokens'],out['all_pairs'],out['nominated_pairs'],out['eligible_leaves'],out['selected_cycles'],out['active_cycles'])==(len(ts),len(ps),len(np),N,len(expected_cycles),len(active))
  status='CAPACITY_STOP' if len(mobile)<5 else ('ROBUST_POSITIVE_RESIDUAL' if delta>0 and loo>0 else 'NONCONFIRMING_OR_FRAGILE');assert out['status']==status
  checks[reader]={'packing':'PASS_REVERSE_DISTANCE_GREEDY','margins':'PASS_EACH_AND_ALL_FLIPS','moments':'PASS_PAIRWISE_COVARIANCE','decision':status}
 assert result['status']==result['readers']['ZL3b']['status']
 validation={'status':'PASS','checks':checks,'limits':'Checks software, old source consistency, margin preservation and restricted-orbit moments; no independent transcription or scientific meaning confirmation.'}
 (B/'artifacts/VALIDATION.json').write_text(json.dumps(validation,indent=2)+'\n');print(json.dumps(validation,indent=2))
if __name__=='__main__':main()
