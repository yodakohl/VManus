"""Independent source geometry and direct per-fold exact label-refit validation."""
import collections,hashlib,itertools,json,random,re
from fractions import Fraction as Q
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]
def read(n):return json.loads((E/'artifacts'/n).read_text())
def num(q):return dict(value=float(q),exact=str(q))
s=json.loads((E/'src/SPEC.json').read_text());raw=(ROOT/s['source']).read_bytes();assert hashlib.sha256(raw).hexdigest()==s['source_sha256'];source=json.loads(raw);events=[];forms={p+'e'+k+'y' for p,k in itertools.product(['ch','sh'],['cth','ckh'])}|{p+k+'ey' for p,k in itertools.product(['ch','sh'],['cth','ckh'])}
for line in source['lines']:
 m=line['metadata'];assert m['edition']=='ZL3b' and m['page'] in s['allowed_selectors'] and not m['page'].startswith('f84');groups=[dict(zip(source['group_columns'],g)) for g in line['groups']]
 for i,t in enumerate(groups):
  match=re.fullmatch(r'(ch|sh)(e?)(cth|ckh)(e?)y',t['ivtff_group_raw'])
  if match is None or len(match[2])+len(match[4])!=1 or i==0 or i+1==len(groups):continue
  a,b=groups[i-1],groups[i+1]
  if any(re.fullmatch('[a-z]+',g['ivtff_group_raw']) is None or g['ivtff_group_raw'] in forms for g in (a,b)):continue
  if int(t['source_group_index'])-int(a['source_group_index'])!=1 or int(b['source_group_index'])-int(t['source_group_index'])!=1:continue
  if not all(v=='DEFINITE_SPACE' for v in [a['right_separator'],t['left_separator'],t['right_separator'],b['left_separator']]):continue
  f=int(re.match(r'f([0-9]+)',m['page'])[1]);idx=int(t['source_group_index']);count=int(m['source_group_count']);assert 1<=idx<=count;half='EARLY' if idx<=Q(count,2) else 'LATE';key=[f,m['page'],m['kind'],m['section'],m['hand'],match[1],match[3],half]
  events.append(dict(id=t['source_group_id'],locus=m['locus'],word=t['ivtff_group_raw'],label='OUTER' if match[2] else 'INNER',folio=f,prefix=match[1],kernel=match[3],cell_key=key,start_index=idx,group_count=count,left=a['ivtff_group_raw'],right=b['ivtff_group_raw']))
events.sort(key=lambda x:x['id']);assert events==read('EVENTS.json');assert len({e['id'] for e in events})==len(events)
grouped=collections.defaultdict(list)
for e in events:grouped[json.dumps(e['cell_key'],separators=(',',':'))].append(e)
cells=[dict(key=json.loads(key),events=ev,mixed=any(e['label']=='OUTER' for e in ev) and any(e['label']=='INNER' for e in ev)) for key,ev in sorted(grouped.items())];assert cells==read('CELLS.json');mixed=[c for c in cells if c['mixed']];folds=sorted({(c['key'][0],c['key'][6]) for c in mixed});fs={k:sorted({f for f,kk in folds if kk==k}) for k in ['cth','ckh']};training=[dict(folio=f,kernel=k,training_folios=sorted({c['key'][0] for c in mixed if c['key'][0]!=f and c['key'][6]!=k})) for f,k in folds];gates=dict(evaluation_folios=len({f for f,k in folds})>=8,each_kernel=all(len(v)>=3 for v in fs.values()),each_training_fold=bool(folds) and all(len(t['training_folios'])>=2 for t in training));cap=dict(pass_all=all(gates.values()),gates=gates,evaluation_folios=sorted({f for f,k in folds}),folios_by_kernel=fs,training_folds=training,mixed_cells=len(mixed),all_cells=len(cells));result=read('RESULT.json');assert result['capacity']==cap and result['events']==len(events)
def independent(flips,detail=False):
 output=[]
 for f,k in folds:
  train=[c for c in mixed if c['key'][0]!=f and c['key'][6]!=k];weights={side:collections.defaultdict(Q) for side in ['left','right']}
  for c in train:
   for side in ['left','right']:
    outer=collections.Counter();inner=collections.Counter()
    for e in c['events']:
     isouter=(e['label']=='OUTER')!=(c['key'][0] in flips);(outer if isouter else inner)[e[side]]+=1
    for v in set(outer)|set(inner):weights[side][v]+=(Q(outer[v],sum(outer.values()))-Q(inner[v],sum(inner.values())))/len(train)
  cellrows=[]
  for c in mixed:
   if c['key'][0]!=f or c['key'][6]!=k:continue
   es=[];outer=[];inner=[]
   for e in c['events']:
    label='OUTER' if ((e['label']=='OUTER')!=(f in flips)) else 'INNER';q=(weights['left'].get(e['left'],Q(0))+weights['right'].get(e['right'],Q(0)))/2;(outer if label=='OUTER' else inner).append(q);es.append(dict(id=e['id'],label=label,score=num(q),known={side:e[side] in weights[side] for side in ['left','right']}))
   wins=0;ties=0
   for a in outer:
    for b in inner:wins+=a>b;ties+=a==b
   auc=Q(2*wins+ties,2*len(outer)*len(inner));row=dict(key=c['key'],auc=num(auc))
   if detail:row['events']=es
   cellrows.append(row)
  mean=sum((Q(x['auc']['exact']) for x in cellrows),Q(0))/len(cellrows);row=dict(folio=f,kernel=k,auc=num(mean),cells=cellrows)
  if detail:row['model']=dict(training_cells=len(train),training_folios=sorted({c['key'][0] for c in train}),weights={side:{v:str(q) for v,q in sorted(ww.items())} for side,ww in weights.items()})
  output.append(row)
 kernels={k:sum((Q(x['auc']['exact']) for x in output if x['kernel']==k),Q(0))/sum(x['kernel']==k for x in output) for k in ['cth','ckh']};overall=sum(kernels.values(),Q(0))/2
 return dict(overall=num(overall),kernels={k:num(q) for k,q in kernels.items()},folds=output) if detail else overall
if not cap['pass_all']:
 assert result['status']=='CAPACITY_STOP_NO_MODEL_OR_NULL';assert not (E/'artifacts/OBSERVED.json').exists() and not (E/'artifacts/NULL.json').exists()
else:
 observed=independent(set(),True);assert observed==read('OBSERVED.json');stat=Q(observed['overall']['exact']);null=read('NULL.json');folios=sorted({c['key'][0] for c in mixed});assert null['folios']==folios and null['fixed_folio']==folios[0] and null['free_folios']==folios[1:];assert independent(set(folios))==stat
 exact=len(folios)<=12;assert null['exact_enumeration']==exact;rng=random.Random(854);patterns=list(itertools.product([0,1],repeat=len(folios)-1)) if exact else [[rng.getrandbits(1) for f in folios[1:]] for _ in range(999)];assert len(patterns)==len(null['patterns']);tail=0
 for bits,row in zip(patterns,null['patterns']):
  assert list(bits)==row['bits'];flips={f for f,b in zip(folios[1:],bits) if b};q=independent(flips);assert row['auc']==num(q) and row['at_least_observed']==(q>=stat);tail+=q>=stat
 p=Q(tail,len(patterns)) if exact else Q(tail+1,1000);assert null['p']==num(p) and null['tail']==tail;success=stat>=Q('0.65') and all(Q(v['exact'])>Q(1,2) for v in observed['kernels'].values()) and p<=Q('0.01');assert result['status']==('NARROW_CROSS_KERNEL_TRANSFER_PASS' if success else 'FIXED_CROSS_KERNEL_COMPARATOR_FAIL');assert result['overall']==observed['overall'] and result['kernels']==observed['kernels'] and result['null_p']==num(p) and result['null_patterns']==len(patterns)
(E/'artifacts/VALIDATION.json').write_text(json.dumps(dict(status='PASS_INDEPENDENT_SOURCE_CELLS_CAPACITY_AND_EXACT_FULL_NULL_REFIT',events=len(events),mixed_cells=len(mixed),model_and_null_executed=cap['pass_all'],semantic_validation=False),indent=2)+'\n');print('PASS')
