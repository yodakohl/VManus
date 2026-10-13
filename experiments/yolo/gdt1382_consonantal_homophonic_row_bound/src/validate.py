#!/usr/bin/env python3
"""Independent homophonic within-row bound. Controls never load native inputs."""
import argparse,collections,gzip,hashlib,importlib.util,itertools,json
from pathlib import Path
B=Path(__file__).resolve().parents[1];ROOT=B.parents[2]
PREVIOUS=ROOT/'experiments/yolo/gdt1380_consonantal_context_cost_bound'
CONSONANTS='bcdfghjklmnpqrstvwxyz';ALPHABET=CONSONANTS+' ';FIXED={' ','^'}

def load(p):
 p=Path(p);raw=p.read_bytes();return json.loads(gzip.decompress(raw) if p.suffix=='.gz' else raw)

def fixed_context_cost(context,counts,assignment,targets,cost):
 assert set(assignment)==set(context)-FIXED and set(assignment.values())<=set(targets)
 targetcontext=tuple(assignment.get(x,x) for x in context)
 total=counts.get(' ',0)*cost(targetcontext,' ')
 total+=sum(counts.get(x,0)*cost(targetcontext,value) for x,value in assignment.items())
 # No exclusions/reservations: a distinct successor may share an anchored image.
 free=sum(n for x,n in counts.items() if x!=' ' and x not in assignment)
 total+=free*min(cost(targetcontext,t) for t in targets)
 return total,targetcontext

def row_minimum(context,counts,targets,cost):
 symbols=sorted(set(context)-FIXED)
 return min(fixed_context_cost(context,counts,dict(zip(symbols,values)),targets,cost) for values in itertools.product(targets,repeat=len(symbols)))

def freely_relaxed(context,counts,targets,cost):
 domains=[[x] if x in FIXED else targets for x in context]
 ordinary=sum(n for x,n in counts.items() if x!=' ')
 return min(counts.get(' ',0)*cost(tc,' ')+ordinary*min(cost(tc,t) for t in targets) for tc in itertools.product(*domains))

def controls():
 targets=['A','B'];source=['x','y','z']
 cases=[(('x','x'),{'x':2,'y':1}),(('x','y'),{'z':3}),(('x','y'),{'x':2,'y':1,' ':3}),(('^','x'),{'x':1,'y':4}),((' ','x'),{'x':1,'z':1,' ':1}),(('^','^'),{'x':3,'y':2}),((' ',' '),{'z':2})]
 for context,counts in cases:
  cost=lambda tc,t:((ord(tc[0])*13+ord(tc[1])*7+ord(t)*11)%37)+1
  bound,_=row_minimum(context,counts,targets,cost);symbols=sorted((set(context)|set(counts))-FIXED)
  brute=[]
  for values in itertools.product(targets,repeat=len(symbols)):
   assignment=dict(zip(symbols,values));tc=tuple(assignment.get(x,x) for x in context)
   brute.append(sum(n*cost(tc,assignment.get(x,x)) for x,n in counts.items()))
  assert bound==min(brute) and bound>=freely_relaxed(context,counts,targets,cost)
 # A normalized three-output probability table, with exact integer bit costs.
 # For repeated target context: ownletter p=1/4, otherletter p=1/2, SPACEp=1/4.
 def strict_cost(tc,t):
  if tc[0]==tc[1] and tc[0] in targets:return 2 if t==tc[0] or t==' ' else 1
  return 1 if t==' ' else 2
 assert row_minimum(('x','x'),{'x':1},targets,strict_cost)[0]==2
 assert freely_relaxed(('x','x'),{'x':1},targets,strict_cost)==1
 # A collision can be the true row optimum; forbidding it would overestimate.
 def collision_cost(tc,t):
  if tc[0]==tc[1] and tc[0] in targets:return 1 if t==tc[0] else 2
  return 1 if t==' ' else 2
 assert row_minimum(('x','y'),{'x':1,'y':1},targets,collision_cost)[0]==2
 injective=min(fixed_context_cost(('x','y'),{'x':1,'y':1},dict(zip(['x','y'],values)),targets,collision_cost)[0] for values in itertools.permutations(targets))
 assert injective==4
 # A free next symbol must be allowed to reuse an anchored context image.
 assert fixed_context_cost(('^','x'),{'y':3},{'x':'A'},targets,lambda tc,t:1 if t=='A' else 9)[0]==3
 streams=[['x','y','z',' ','x'],['z','x','x']];counts=collections.defaultdict(collections.Counter)
 for stream in streams:
  history=('^','^')
  for symbol in stream:counts[history][symbol]+=1;history=(history[1],symbol)
 cost=lambda tc,t:((ord(tc[0])*17+ord(tc[1])*3+ord(t)*5)%29)+1
 bound=sum(row_minimum(ctx,c,targets,cost)[0] for ctx,c in counts.items());totals=[]
 for values in itertools.product(targets,repeat=len(source)):
  key=dict(zip(source,values));totals.append(sum(n*cost(tuple(key.get(x,x) for x in ctx),key.get(symbol,symbol)) for ctx,c in counts.items() for symbol,n in c.items()))
 assert bound<=min(totals)
 return {'exhaustive_local_rows':7,'all_global_maps_including_collisions':8,'more_source_than_target_symbols':'PASS','strict_improvement_bits':[1,2],'collision_vs_injective_bits':[2,4],'context_image_reuse':'PASS','SPACE_BOS':'PASS'}

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--controls-only',action='store_true');args=parser.parse_args();check=controls()
 if args.controls_only:
  print(json.dumps(check));return
 lock=load(B/'src/REGISTRATION_LOCK.json')
 for path,digest in lock['hashes'].items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest,path
 helper_path=PREVIOUS/'src/validate.py';spec=importlib.util.spec_from_file_location('independent1380_intervals',helper_path);helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
 corpus=load(PREVIOUS/'artifacts/CORPUS.json.gz');models=load(PREVIOUS/'artifacts/MODEL_COUNTS.json.gz');old=load(PREVIOUS/'artifacts/RESULT.json');scale=2**32
 assert old['scale']==scale and set(corpus)=={'ZL3b','IT2a','RF1b'} and len(models)==6
 modelcosts={}
 for name in sorted(models):
  counts={tuple(r['context']):r['counts'] for r in models[name]['rows']};table={}
  for a,b in itertools.product(sorted(set(ALPHABET+'^')),repeat=2):
   row=counts.get((a,b),[0]*22);denominator=2*sum(row)+22
   table[(a,b)]={symbol:helper.ticks(denominator,2*n+1,scale)[0] for symbol,n in zip(ALPHABET,row)}
  modelcosts[name]=table
 result={'status':'HOMOPHONIC_CONTEXT_BOUND','scale':scale,'reverse_lower':0,'readers':{}}
 keytick=helper.ticks(21,1,scale);selectortick=helper.ticks(6,1,scale);checked=0
 for reader in ('ZL3b','IT2a','RF1b'):
  source=corpus[reader];m=len(source['active']);assert source['events']>0
  kt=helper.kt_ticks(source['contexts'],m+1,scale)
  if reader=='IT2a':assert kt==(old['readers'][reader]['kt_lo'],old['readers'][reader]['kt_hi'])
  outcome={'lines':len(source['lines']),'groups':source['groups'],'events':source['events'],'active_symbols':source['active'],'context_count':len(source['contexts']),'kt_lo':kt[0],'kt_hi':kt[1],'key_lo':m*keytick[0],'key_hi':m*keytick[1],'selector_lo':selectortick[0],'selector_hi':selectortick[1],'packs':{}}
  for name,table in modelcosts.items():
   cost=lambda ctx,symbol:table[ctx][symbol]
   rows=[];payload=0
   for entry in source['contexts']:
    context=tuple(entry['context']);counts=entry['counts'];assert '^' not in counts and all(n>0 for n in counts.values())
    lower,targetcontext=row_minimum(context,counts,sorted(CONSONANTS),cost)
    # This is an additional internal mathematical check, not an injective comparison.
    assert lower>=freely_relaxed(context,counts,sorted(CONSONANTS),cost)
    rows.append({'context':list(context),'target_context':list(targetcontext),'lower':lower});payload+=lower;checked+=1
   paid=payload+outcome['key_lo']+outcome['selector_lo'];margin=paid-outcome['kt_hi']
   outcome['packs'][name]={'payload_lower':payload,'paid_lower':paid,'margin_lower':margin,'status':'CERTIFIED_NO_KEY_BEATS_MATCHED_KT' if margin>0 else 'BOUND_INCONCLUSIVE','rows':rows}
  result['readers'][reader]=outcome
 actual=load(B/'artifacts/RESULT.json');assert result==actual,'homophonic row certificates or cost accounting differ'
 receipt={'status':'PASS','source_free_controls':check,'row_certificates':checked,'readers':{reader:{'active_symbols':data['active_symbols'],'events':data['events'],'pack_statuses':{name:p['status'] for name,p in data['packs'].items()}} for reader,data in result['readers'].items()},'reverse_lower':0,'interval_helper_sha256':hashlib.sha256(helper_path.read_bytes()).hexdigest(),'method':'Independent with-replacement partialcontextmap enumeration and full free-successor reuse, exactinteger row minimization; immutable1380independent Decimal80ticks/KT only; no1382primaryimports or new native extraction.'}
 (B/'artifacts/VALIDATION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
