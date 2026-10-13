from pathlib import Path
from itertools import permutations,product
import gzip,hashlib,importlib.util,json
B=Path(__file__).resolve().parents[1];R=B.parents[2];OLD=R/'experiments/yolo/gdt1380_consonantal_context_cost_bound';C='bcdfghjklmnpqrstvwxyz';SCALE=2**32

def read(p):
 raw=p.read_bytes();return json.loads(gzip.decompress(raw) if p.suffix=='.gz' else raw)
def save(n,x):(B/'artifacts'/n).write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def helper():
 s=importlib.util.spec_from_file_location('frozen1380_arithmetic',OLD/'src/run.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def bound(ctx,counts,table,alphabet=C):
 anchors=sorted(set(ctx)-{'^',' '});best=None
 for targets in permutations(alphabet,len(anchors)):
  partial=dict(zip(anchors,targets));dest=tuple(partial.get(x,x) for x in ctx);cost=table[dest];reserved=set(targets)
  fixed=counts.get(' ',0)*cost[len(alphabet)]+sum(counts.get(x,0)*cost[alphabet.index(y)] for x,y in partial.items())
  weights=sorted([n for x,n in counts.items() if x!=' ' and x not in partial and n>0],reverse=True)
  remaining=sorted(cost[j] for j,s in enumerate(alphabet) if s not in reserved)
  assert len(weights)<=len(remaining)
  value=fixed+sum(x*y for x,y in zip(weights,remaining));candidate=(value,dest)
  if best is None or candidate<best:best=candidate
 return best

def controls():
 alpha='xy';tab={ctx:[0,0,0] for ctx in product(alpha+' ^',repeat=2)}
 tab[('x','x')]=[0,9,0];tab[('y','y')]=[9,0,0]
 assert bound(('a','a'),{'b':1},tab,alpha)[0]==9
 # A context symbol absent from next counts still reserves its target.
 tab[('x','^')]=[0,8,0];tab[('y','^')]=[8,0,0]
 assert bound(('a','^'),{'b':1},tab,alpha)[0]==8
 checks=0;alpha='xyz';states=alpha+' ^';table={c:[(i+1)*(j+2)+(k*k+3*k)%7 for k in range(4)] for i,a in enumerate(states) for j,b in enumerate(states) for c in [(a,b)]}
 for ctx in [('a','a'),('a','b'),('^','a'),(' ','a'),('^','^'),(' ',' ')]:
  for counts in [{'a':2,'b':1,'c':3,' ':1},{'c':5},{'a':4}]:
   relaxed=[];actual=[]
   for dest in product(*[(s,) if s in ('^',' ') else alpha for s in ctx]):
    costs=table[dest];w=sorted([v for k,v in counts.items() if k!=' '],reverse=True);relaxed.append(sum(a*b for a,b in zip(w,sorted(costs[:3])))+counts.get(' ',0)*costs[3])
   for vals in permutations(alpha):
    f=dict(zip('abc',vals));dest=tuple(f.get(s,s) for s in ctx);v=sum(n*table[dest][3 if s==' ' else alpha.index(f[s])] for s,n in counts.items());actual.append(v)
   got=bound(ctx,counts,table,alpha)[0];assert min(relaxed)<=got==min(actual);checks+=len(actual)
 return {'status':'PASS','global_injections_checked':checks,'strict_improvement':9,'zero_successor_anchor_reserved':True,'SPACE_BOS_and_repeated_context':True}

def main():
 for p,h in read(B/'src/REGISTRATION_LOCK.json')['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 save('CONTROLS.json',controls());m=helper();old=read(OLD/'artifacts/RESULT.json');src=read(OLD/'artifacts/CORPUS.json.gz')['IT2a'];models=read(OLD/'artifacts/MODEL_COUNTS.json.gz');baseline=old['readers']['IT2a']
 assert old['scale']==SCALE and len(src['active'])==21
 selected=('latin','middle_french');assert {p for p,v in baseline['packs'].items() if v['status']=='BOUND_INCONCLUSIVE'}==set(selected)
 result={}
 for pack in selected:
  model={tuple(x['context']):x['counts'] for x in models[pack]['rows']};table={}
  for ctx in product(C+' ^',repeat=2):
   v=model.get(ctx,[0]*22);table[ctx]=[m.ticks(2*n+1,2*sum(v)+22)[0] for n in v]
  oldrows={tuple(x['context']):x for x in baseline['packs'][pack]['rows']};rows=[];payload=0
  for row in src['contexts']:
   ctx=tuple(row['context']);value,dest=bound(ctx,row['counts'],table);previous=oldrows[ctx]['lower'];assert value>=previous
   rows.append({'context':list(ctx),'target_context':list(dest),'lower':value,'old_lower':previous,'increase':value-previous});payload+=value
  paid=payload+baseline['key_lo']+baseline['selector_lo'];margin=paid-baseline['kt_hi']
  result[pack]={'payload_lower':payload,'paid_lower':paid,'margin_lower':margin,'status':'CERTIFIED_NO_KEY_BEATS_MATCHED_KT' if margin>0 else 'BOUND_INCONCLUSIVE','rows':rows}
  print(pack,'new_margin_bits',margin/SCALE,'increase_bits',(payload-baseline['packs'][pack]['payload_lower'])/SCALE,flush=True)
 prior=[v for k,v in baseline['packs'].items() if k not in selected];assert len(prior)==4 and all(v['margin_lower']>0 for v in prior)
 save('RESULT.json',{'status':'ROW_CONSISTENT_CONTEXT_BOUND','reader':'IT2a','scale':SCALE,'kt_upper':baseline['kt_hi'],'key_lower':baseline['key_lo'],'selector_lower':baseline['selector_lo'],'packs':result,'combined_six_pack_status':'ALL_PACKS_CERTIFIED' if all(v['margin_lower']>0 for v in result.values()) else 'PARTIAL_CERTIFIED_BOUNDS'})
if __name__=='__main__':main()
