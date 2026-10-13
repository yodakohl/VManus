"""Certified optimistic cost bound for a fixed many-to-one consonantal map."""
from pathlib import Path
from itertools import product
from collections import Counter,defaultdict
import argparse,gzip,hashlib,importlib.util,json
B=Path(__file__).resolve().parents[1];R=B.parents[2]
OLD=R/'experiments/yolo/gdt1380_consonantal_context_cost_bound'
C='bcdfghjklmnpqrstvwxyz';SCALE=2**32;FIXED={'^',' '}

def read(p):
 raw=p.read_bytes();return json.loads(gzip.decompress(raw) if p.suffix=='.gz' else raw)
def save(n,x):(B/'artifacts'/n).write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def helper():
 s=importlib.util.spec_from_file_location('frozen1380_arithmetic',OLD/'src/run.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def bound(ctx,counts,table,alphabet=C):
 anchors=sorted(set(ctx)-FIXED);free=sum(n for x,n in counts.items() if x not in FIXED and x not in anchors);best=None
 for targets in product(alphabet,repeat=len(anchors)):
  partial=dict(zip(anchors,targets));dest=tuple(partial.get(x,x) for x in ctx);cost=table[dest]
  value=counts.get(' ',0)*cost[len(alphabet)]+sum(counts.get(x,0)*cost[alphabet.index(y)] for x,y in partial.items())+free*min(cost[:len(alphabet)])
  candidate=(value,dest)
  if best is None or candidate<best:best=candidate
 assert best is not None
 return best

def controls():
 alpha='xy';states=alpha+' ^';source='abc';checks=0
 contexts=[('a','a'),('a','b'),('^','a'),(' ','a'),('^','^'),(' ',' ')]
 for seed in range(10):
  table={ctx:[((i+seed+1)*7+(j+seed)*3+k*11+i*j*k)%31 for k in range(3)] for i,a in enumerate(states) for j,b in enumerate(states) for ctx in [(a,b)]}
  for ctx in contexts:
   for counts in [{'a':2,'b':1,'c':3,' ':1},{'c':5},{'a':4},{' ':2}]:
    exact=[]
    for values in product(alpha,repeat=len(source)):
     key=dict(zip(source,values));dest=tuple(key.get(s,s) for s in ctx)
     exact.append(sum(n*table[dest][2 if s==' ' else alpha.index(key[s])] for s,n in counts.items()))
    assert bound(ctx,counts,table,alpha)[0]==min(exact);checks+=len(exact)
 # Same source symbol cannot be assigned different images in context and output.
 table={ctx:[10 if ctx[0]==ctx[1]==t else 0 for t in alpha+' '] for ctx in product(states,repeat=2)}
 assert bound(('a','a'),{'a':1},table,alpha)[0]==10
 assert min(min(table[ctx][:2]) for ctx in product(alpha,repeat=2))==0
 # Distinct context signs may collide and a free successor may reuse that image.
 table={ctx:[0 if ctx==('x','x') and t=='x' else 100 for t in alpha+' '] for ctx in product(states,repeat=2)}
 assert bound(('a','b'),{'c':1},table,alpha)==(0,('x','x'))
 # Multirow lower bound versus every global mapping, three source signs/two targets.
 rows=defaultdict(Counter)
 for stream in ['ab ca','caba']:
  history=('^','^')
  for s in stream:rows[history][s]+=1;history=(history[1],s)
 table={ctx:[(i*3+j*7+k*11)%29 for k in range(3)] for i,a in enumerate(states) for j,b in enumerate(states) for ctx in [(a,b)]}
 lower=sum(bound(ctx,c,table,alpha)[0] for ctx,c in rows.items());actual=[]
 for values in product(alpha,repeat=3):
  key=dict(zip(source,values));actual.append(sum(n*table[tuple(key.get(s,s) for s in ctx)][2 if x==' ' else alpha.index(key[x])] for ctx,c in rows.items() for x,n in c.items()))
 assert lower<=min(actual)
 return {'status':'PASS','local_global_maps_checked':checks,'global_multicontext_maps':len(actual),'more_source_than_target':True,'same_symbol_identity_strict_improvement':10,'distinct_context_collision_and_successor_reuse':True,'SPACE_BOS':True}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--controls-only',action='store_true');args=ap.parse_args();check=controls()
 if args.controls_only:print(json.dumps(check));return
 for p,h in read(B/'src/REGISTRATION_LOCK.json')['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 save('CONTROLS.json',check);m=helper();old=read(OLD/'artifacts/RESULT.json');data=read(OLD/'artifacts/CORPUS.json.gz');models=read(OLD/'artifacts/MODEL_COUNTS.json.gz')
 assert set(data)=={'IT2a','ZL3b','RF1b'}
 assert set(models)=={'latin','medieval_czech','middle_french','middle_high_german','old_hungarian','old_italian_tuscan'}
 tables={}
 for pack in sorted(models):
  model={tuple(x['context']):x['counts'] for x in models[pack]['rows']};table={}
  for ctx in product(C+' ^',repeat=2):
   v=model.get(ctx,[0]*22);table[ctx]=[m.ticks(2*n+1,2*sum(v)+22)[0] for n in v]
  tables[pack]=table
 result={}
 for ed in ('ZL3b','IT2a','RF1b'):
  src=data[ed];size=len(src['active']);ktlo,kthi=m.kt(src['contexts'],size+1);kl,kh=m.ticks(1,21);sl,sh=m.ticks(1,6)
  if ed=='IT2a':assert (ktlo,kthi)==(old['readers'][ed]['kt_lo'],old['readers'][ed]['kt_hi'])
  r={'lines':len(src['lines']),'groups':src['groups'],'events':src['events'],'active_symbols':src['active'],'context_count':len(src['contexts']),'kt_lo':ktlo,'kt_hi':kthi,'key_lo':size*kl,'key_hi':size*kh,'selector_lo':sl,'selector_hi':sh,'packs':{}}
  for pack,table in tables.items():
   rows=[];payload=0
   for row in src['contexts']:
    ctx=tuple(row['context']);value,dest=bound(ctx,row['counts'],table);payload+=value;rows.append({'context':list(ctx),'target_context':list(dest),'lower':value})
   paid=payload+r['key_lo']+r['selector_lo'];margin=paid-r['kt_hi'];r['packs'][pack]={'payload_lower':payload,'paid_lower':paid,'margin_lower':margin,'status':'CERTIFIED_NO_KEY_BEATS_MATCHED_KT' if margin>0 else 'BOUND_INCONCLUSIVE','rows':rows}
  result[ed]=r;print(ed,{p:round(v['margin_lower']/SCALE,6) for p,v in r['packs'].items()},flush=True)
 save('RESULT.json',{'status':'HOMOPHONIC_CONTEXT_BOUND','scale':SCALE,'reverse_lower':0,'readers':result})
if __name__=='__main__':main()
