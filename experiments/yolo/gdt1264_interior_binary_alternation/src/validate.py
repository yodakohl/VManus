import collections,gzip,hashlib,itertools,json,re
from fractions import Fraction
from pathlib import Path
import numpy as np
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def main():
 s=json.loads((B/'src/SPEC.json').read_text());fit=json.loads((B/'artifacts/TRAIN.json').read_text());out=json.loads((B/'artifacts/RESULT.json').read_text())
 for p,h in json.loads((B/'src/REGISTRATION_LOCK.json').read_text())['hashes'].items():assert hashlib.sha256((B/p).read_bytes()).hexdigest()==h
 for x in s['inputs']:assert hashlib.sha256((R/x['path']).read_bytes()).hexdigest()==x['sha256']
 assert hashlib.sha256((B/'artifacts/TRAIN.json').read_bytes()).hexdigest()==json.loads((B/'artifacts/TRAIN_LOCK.json').read_text())['train_sha256']
 data=json.loads(gzip.decompress((R/s['source']).read_bytes()));folio=lambda r:int(re.match(r'f([0-9]+)',r['page']).group(1))
 for reader in s['readers']:assert all(not r['page'].startswith('f84') and r['page']!='f116v' for r in data[reader])
 train=[r for r in data[s['primary']] if folio(r)%2==1 and len(r['units'])>=s['minimum_interior_units']+2];assert fit['source_ids']==[r['id'] for r in train] and fit['groups']==len(train)
 units=sorted({u for row in train for u in row['units'][1:-1]});assert units==fit['active_units'];n=len(units);w=collections.defaultdict(Fraction)
 for row in train:
  x=row['units'][1:-1]
  for i in range(len(x)-1):
   if x[i]!=x[i+1]:w[tuple(sorted([x[i],x[i+1]]))]+=1
  # Position-pair expansion independently reproduces the bag expectation.
  for i in range(len(x)):
   for j in range(i+1,len(x)):
    if x[i]!=x[j]:w[tuple(sorted([x[i],x[j]]))]-=Fraction(2,len(x))
 matrix=np.zeros((n,n),dtype=np.int64)
 for e in fit['weights']:
  key=(e['a'],e['b']);assert Fraction(*e['exact'])==w[key];q=round(w[key]*s['weight_scale']);assert q==e['quantized'];i,j=units.index(key[0]),units.index(key[1]);matrix[i,j]=matrix[j,i]=q
 assert len(fit['weights'])==n*(n-1)//2 and matrix.tolist()==fit['matrix']
 # Full independent binary-mask enumeration against Gray-code C++ optimizer.
 masks=np.arange(2,1<<n,2,dtype=np.uint32);scores=np.zeros(len(masks),dtype=np.int64)
 for i in range(n):
  for j in range(i+1,n):
   q=int(matrix[i,j])
   if q:scores+=((((masks>>i)^(masks>>j))&1).astype(np.int64))*q
 best=int(scores.max());indices=np.flatnonzero(scores==best);bestmask=int(masks[indices[0]])
 assert fit['optimizer']=={'best_score':best,'best_mask':bestmask,'ties':len(indices),'partitions':len(masks)}
 labels={u:(bestmask>>i)&1 for i,u in enumerate(units)};assert labels==fit['labels']==out['train_labels'];assert Fraction(*fit['exact_selected_score'])==sum((v for (a,b),v in w.items() if labels[a]!=labels[b]),Fraction(0))
 events=json.loads(gzip.decompress((B/'artifacts/EVENTS.json.gz').read_bytes()));actual_events=[];checks=[]
 for reader in s['readers']:
  seen={tuple(r['units']) for r in data[reader] if folio(r)%2==1};test=[r for r in data[reader] if folio(r)%2==0]
  for cohort in s['cohorts']:
   report=next(r for r in out['reports'] if r['reader']==reader and r['cohort']==cohort);counts=collections.Counter();leaves=collections.defaultdict(list)
   for row in test:
    if cohort=='UNSEEN_WHOLE' and tuple(row['units']) in seen:continue
    counts['source_groups']+=1;x=row['units'][1:-1]
    if len(x)<s['minimum_interior_units']:counts['too_short']+=1;continue
    counts['eligible_groups']+=1
    if any(u not in labels for u in x):counts['unknown_unit_groups']+=1;actual_events.append({'reader':reader,'cohort':cohort,'id':row['id'],'status':'UNSEEN_TRAIN_UNIT','units':x});continue
    y=list(map(labels.__getitem__,x));o=sum(y[i]!=y[i+1] for i in range(len(y)-1));expectation=Fraction(sum(y[i]!=y[j] for i in range(len(y)) for j in range(i+1,len(y)))*2,len(y));f=folio(row);leaves[f].append((len(y)-1,o,expectation));counts['scorable_groups']+=1
    actual_events.append({'reader':reader,'cohort':cohort,'id':row['id'],'page':row['page'],'leaf':f,'whole_units':row['units'],'units':x,'classes':y,'observed':o,'expected':[expectation.numerator,expectation.denominator],'status':'SCORED'})
   assert counts==collections.Counter(report['counts']);effects=[]
   assert [r['leaf'] for r in report['leaves']]==sorted(leaves)
   for rec in report['leaves']:
    vals=leaves[rec['leaf']];edges=sum(t[0] for t in vals);obs=sum(t[1] for t in vals);expected=sum((t[2] for t in vals),Fraction(0));excess=obs-expected;effect=excess/edges;effects.append(effect)
    assert rec['groups']==len(vals) and rec['edges']==edges and rec['observed']==obs and Fraction(*rec['expected'])==expected and Fraction(*rec['excess'])==excess and Fraction(*rec['effect'])==effect
   mean=sum(effects,Fraction(0))/len(effects) if effects else Fraction(0);positive=sum(e>0 for e in effects);pf=Fraction(positive,len(effects)) if effects else Fraction(0)
   assert report['scorable_leaves']==len(effects) and report['positive_leaves']==positive and report['zero_leaves']==effects.count(Fraction(0)) and Fraction(*report['mean_effect'])==mean and Fraction(*report['positive_fraction'])==pf
   passed=len(effects)>=s['minimum_leaves'] and pf>=Fraction(*s['minimum_positive_leaf_fraction']) and mean>=Fraction(*s['minimum_mean_excess']);assert passed==report['gate_pass'];checks.append({'reader':reader,'cohort':cohort,'scorable_groups':counts['scorable_groups'],'leaves':len(effects),'positive_leaves':positive,'mean_effect':float(mean),'gate_pass':passed})
 assert actual_events==events
 expected_status='BINARY_INTERIOR_ORDER_LEAD' if all(x['gate_pass'] for x in checks if x['reader']==s['primary']) else 'FIXED_BINARY_INTERIOR_LEAD_NOT_ESTABLISHED';assert out['status']==expected_status
 val={'status':'PASS','exact_quantized_partitions_verified':len(masks),'tied_optima':len(indices),'evaluation_checks':checks,'event_rows_verified':len(events),'implementation':'Independent position-pair bag expectation, vectorized exhaustive binary masks, raw-source cohort rebuild and exact rational leaf scores; no primary import.','limits':'Numerical and source-account validation, not phonetic truth, independent data confirmation or stage/Markov variance explained.'};(B/'artifacts/VALIDATION.json').write_text(json.dumps(val,indent=2)+'\n');print(json.dumps(val,indent=2))
if __name__=='__main__':main()
