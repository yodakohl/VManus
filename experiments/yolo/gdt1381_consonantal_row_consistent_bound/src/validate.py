#!/usr/bin/env python3
"""Independent context-identity bound; inherited certified arithmetic only."""
import argparse,collections,gzip,hashlib,importlib.util,itertools,json
from pathlib import Path
B=Path(__file__).resolve().parents[1];ROOT=B.parents[2]
PREVIOUS=ROOT/'experiments/yolo/gdt1380_consonantal_context_cost_bound'
CONSONANTS='bcdfghjklmnpqrstvwxyz';ALPHABET=CONSONANTS+' ';FIXED={' ','^'}

def load(p):
 p=Path(p);b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)

def conditioned_row(context,counts,targets,assignment,cost):
 """Cost for one fixed injective map of distinct ordinary context signs."""
 assert set(assignment)==set(context)-FIXED
 assert len(set(assignment.values()))==len(assignment) and set(assignment.values())<=set(targets)
 tc=tuple(assignment.get(x,x) for x in context)
 anchored=set(assignment);reserved=set(assignment.values())
 total=counts.get(' ',0)*cost(tc,' ')
 total+=sum(counts.get(x,0)*cost(tc,t) for x,t in assignment.items())
 weights=sorted((n for x,n in counts.items() if x!=' ' and x not in anchored and n>0),reverse=True)
 available=sorted(cost(tc,t) for t in targets if t not in reserved)
 assert len(weights)<=len(available)
 return total+sum(n*c for n,c in zip(weights,available)),tc

def row_minimum(context,counts,targets,cost):
 ordinary=sorted(set(context)-FIXED);candidates=[]
 for values in itertools.permutations(targets,len(ordinary)):
  candidates.append(conditioned_row(context,counts,targets,dict(zip(ordinary,values)),cost))
 return min(candidates)

def old_relaxed(context,counts,targets,cost):
 domains=[[x] if x in FIXED else targets for x in context]
 weights=sorted((n for x,n in counts.items() if x!=' ' and n>0),reverse=True)
 return min(counts.get(' ',0)*cost(tc,' ')+sum(n*c for n,c in zip(weights,sorted(cost(tc,t) for t in targets))) for tc in itertools.product(*domains))

def controls():
 targets=['A','B','C'];source=['x','y','z'];cases=[(('x','x'),{'x':2,'y':1}),(('x','y'),{'z':3}),(('x','y'),{'x':2,'y':1,' ':3}),(('^','x'),{'x':1,'y':4}),((' ','x'),{'x':1,'z':1,' ':1}),(('^','^'),{'x':3,'y':2}),((' ',' '),{'z':2})]
 for ctx,counts in cases:
  cost=lambda tc,t:((ord(tc[0])*13+ord(tc[1])*7+ord(t)*11)%37)+1
  got,_=row_minimum(ctx,counts,targets,cost);union=sorted((set(ctx)|set(counts))-FIXED)
  actual=[]
  for values in itertools.permutations(targets,len(union)):
   key=dict(zip(union,values));tc=tuple(key.get(x,x) for x in ctx)
   actual.append(sum(n*cost(tc,key.get(x,x)) for x,n in counts.items()))
  assert got==min(actual) and got>=old_relaxed(ctx,counts,targets,cost)
 assert row_minimum(('x','x'),{'x':1},targets,lambda ctx,t:10 if ctx[0]==ctx[1]==t else 0)[0]==10
 assert old_relaxed(('x','x'),{'x':1},targets,lambda ctx,t:10 if ctx[0]==ctx[1]==t else 0)==0
 # Reserve context letters even when neither appears next.
 value,tc=conditioned_row(('x','y'),{'z':1},targets,{'x':'A','y':'B'},lambda ctx,t:{'A':0,'B':1,'C':100,' ':4}[t])
 assert value==100 and tc==('A','B')
 # The same repeated context sign consumes one target and its count is paid once.
 value,_=conditioned_row(('x','x'),{'x':2,'y':1},targets,{'x':'A'},lambda ctx,t:{'A':3,'B':5,'C':7,' ':4}[t]);assert value==11
 streams=[['x','y','z',' ','x'],['z','x','x']];counts=collections.defaultdict(collections.Counter)
 for stream in streams:
  history=('^','^')
  for symbol in stream:counts[history][symbol]+=1;history=(history[1],symbol)
 cost=lambda tc,t:((ord(tc[0])*17+ord(tc[1])*3+ord(t)*5)%29)+1
 bound=sum(row_minimum(ctx,c,targets,cost)[0] for ctx,c in counts.items())
 actual=[]
 for values in itertools.permutations(targets):
  key=dict(zip(source,values));actual.append(sum(n*cost(tuple(key.get(x,x) for x in ctx),key.get(symbol,symbol)) for ctx,c in counts.items() for symbol,n in c.items()))
 assert bound<=min(actual)
 return {'exhaustive_local_rows':len(cases),'global_injections':len(actual),'old_bound_monotonicity':'PASS','zero_next_context_reservation':'PASS','repeated_context_single_payment':'PASS','SPACE_BOS':'PASS','strict_improvement_fixture':'PASS'}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--controls-only',action='store_true');args=ap.parse_args();check=controls()
 if args.controls_only:print(json.dumps(check));return
 lock=load(B/'src/REGISTRATION_LOCK.json')
 for p,h in lock['hashes'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
 # Only the already independently certified immutable interval function is shared.
 path=PREVIOUS/'src/validate.py';spec=importlib.util.spec_from_file_location('gdt1380_independent_intervals',path);arith=importlib.util.module_from_spec(spec);spec.loader.exec_module(arith)
 old=load(PREVIOUS/'artifacts/RESULT.json');corpus=load(PREVIOUS/'artifacts/CORPUS.json.gz')['IT2a'];models=load(PREVIOUS/'artifacts/MODEL_COUNTS.json.gz');prior=old['readers']['IT2a'];scale=old['scale'];assert scale==2**32 and len(corpus['active'])==21
 assert len(corpus['contexts'])==prior['context_count']
 selected=('latin','middle_french');inherited=set(prior['packs'])-set(selected);assert len(inherited)==4
 assert all(prior['packs'][p]['status']=='CERTIFIED_NO_KEY_BEATS_MATCHED_KT' and prior['packs'][p]['margin_lower']>0 for p in inherited)
 result={'status':'ROW_CONSISTENT_CONTEXT_BOUND','reader':'IT2a','scale':scale,'kt_upper':prior['kt_hi'],'key_lower':prior['key_lo'],'selector_lower':prior['selector_lo'],'packs':{},'combined_six_pack_status':None}
 checked=0
 for name in selected:
  rawcounts={tuple(r['context']):r['counts'] for r in models[name]['rows']};table={}
  for a,b in itertools.product(sorted(set(ALPHABET+'^')),repeat=2):
   c=rawcounts.get((a,b),[0]*22);den=2*sum(c)+22
   table[(a,b)]={symbol:arith.ticks(den,2*n+1,scale)[0] for symbol,n in zip(ALPHABET,c)}
  cost=lambda ctx,symbol:table[ctx][symbol]
  oldrows={tuple(r['context']):r['lower'] for r in prior['packs'][name]['rows']};rows=[];payload=0
  for r in corpus['contexts']:
   ctx=tuple(r['context']);counts=r['counts'];minimum,target=row_minimum(ctx,counts,sorted(CONSONANTS),cost)
   oldvalue=old_relaxed(ctx,counts,sorted(CONSONANTS),cost);assert oldvalue==oldrows[ctx] and minimum>=oldvalue
   rows.append({'context':list(ctx),'target_context':list(target),'lower':minimum,'old_lower':oldvalue,'increase':minimum-oldvalue});payload+=minimum;checked+=1
  paid=payload+result['key_lower']+result['selector_lower'];margin=paid-result['kt_upper']
  result['packs'][name]={'payload_lower':payload,'paid_lower':paid,'margin_lower':margin,'status':'CERTIFIED_NO_KEY_BEATS_MATCHED_KT' if margin>0 else 'BOUND_INCONCLUSIVE','rows':rows}
 result['combined_six_pack_status']='ALL_PACKS_CERTIFIED' if all(p['margin_lower']>0 for p in result['packs'].values()) else 'PARTIAL_CERTIFIED_BOUNDS'
 actual=load(B/'artifacts/RESULT.json');assert result==actual,'row certificate or aggregate discrepancy'
 receipt={'status':'PASS','source_free_controls':check,'row_certificates':checked,'readers_recomputed':['IT2a'],'packs_recomputed':list(selected),'inherited_certified_packs':sorted(inherited),'combined_six_pack_status':result['combined_six_pack_status'],'interval_source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'method':'Independent enumeration of injective context partialmaps, anchored payments and residual sortedassignment; all oldrow bounds reproduced and monotonic. Uses unchanged1380independent Decimal80intervals only; no1381primary imports, no new native extraction.'}
 (B/'artifacts/VALIDATION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
