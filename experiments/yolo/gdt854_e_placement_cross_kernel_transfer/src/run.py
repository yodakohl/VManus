import argparse,collections,hashlib,itertools,json,random,re
from fractions import Fraction as Q
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]
def enc(x):return json.dumps(x,sort_keys=True,separators=(',',':'))+'\n'
def save(n,x,check=False):
 p=E/'artifacts'/n
 if check:assert p.read_text()==enc(x),n
 else:p.write_text(enc(x))
def number(q):return dict(value=float(q),exact=str(q))
def extract(source,s):
 forms={p+'e'+k+'y':(p,k,'OUTER') for p,k in itertools.product(s['prefixes'],s['kernels'])};forms.update({p+k+'ey':(p,k,'INNER') for p,k in itertools.product(s['prefixes'],s['kernels'])});events=[]
 for line in source['lines']:
  m=line['metadata'];assert m['edition']=='ZL3b' and m['page'] in s['allowed_selectors'] and not m['page'].startswith('f84');gg=[dict(zip(source['group_columns'],g)) for g in line['groups']]
  for i in range(1,len(gg)-1):
   left,t,right=gg[i-1:i+2];word=t['ivtff_group_raw']
   if word not in forms:continue
   if not all(re.fullmatch('[a-z]+',g['ivtff_group_raw']) and g['ivtff_group_raw'] not in forms for g in [left,right]):continue
   if not all(int(b['source_group_index'])==int(a['source_group_index'])+1 and a['right_separator']==b['left_separator']=='DEFINITE_SPACE' for a,b in [(left,t),(t,right)]):continue
   p,k,label=forms[word];folio=int(re.match(r'f(\d+)',m['page'])[1]);index=int(t['source_group_index']);assert 1<=index<=int(m['source_group_count']);half='EARLY' if 2*index<=int(m['source_group_count']) else 'LATE';key=[folio,m['page'],m['kind'],m['section'],m['hand'],p,k,half]
   events.append(dict(id=t['source_group_id'],locus=m['locus'],word=word,label=label,folio=folio,prefix=p,kernel=k,cell_key=key,start_index=index,group_count=int(m['source_group_count']),left=left['ivtff_group_raw'],right=right['ivtff_group_raw']))
 events.sort(key=lambda e:e['id']);return events
def cells_for(events):
 by=collections.defaultdict(list)
 for e in events:by[json.dumps(e['cell_key'],separators=(',',':'))].append(e)
 return [dict(key=json.loads(k),events=v,mixed={e['label'] for e in v}=={'OUTER','INNER'}) for k,v in sorted(by.items())]
def capacity(cells,s):
 mixed=[c for c in cells if c['mixed']];folds=sorted({(c['key'][0],c['key'][6]) for c in mixed});fs={k:sorted({f for f,kk in folds if kk==k}) for k in s['kernels']};training=[dict(folio=f,kernel=k,training_folios=sorted({c['key'][0] for c in mixed if c['key'][0]!=f and c['key'][6]!=k})) for f,k in folds]
 gates=dict(evaluation_folios=len({f for f,k in folds})>=s['minimum_evaluation_folios'],each_kernel=all(len(v)>=s['minimum_folios_each_kernel'] for v in fs.values()),each_training_fold=bool(folds) and all(len(t['training_folios'])>=s['minimum_training_folios_each_fold'] for t in training))
 return dict(pass_all=all(gates.values()),gates=gates,evaluation_folios=sorted({f for f,k in folds}),folios_by_kernel=fs,training_folds=training,mixed_cells=len(mixed),all_cells=len(cells))
def prepare(cells):
 output=[]
 for c in cells:
  if not c['mixed']:continue
  weights={}
  for side in ['left','right']:
   counts={label:collections.Counter(e[side] for e in c['events'] if e['label']==label) for label in ['OUTER','INNER']};n={label:sum(cc.values()) for label,cc in counts.items()}
   weights[side]={v:Q(counts['OUTER'][v],n['OUTER'])-Q(counts['INNER'][v],n['INNER']) for v in set(counts['OUTER'])|set(counts['INNER'])}
  output.append(dict(cell=c,weights=weights))
 return output
def evaluate(prepared,flipped=frozenset(),detail=False):
 folds=sorted({(x['cell']['key'][0],x['cell']['key'][6]) for x in prepared});foldresults=[]
 for f,k in folds:
  train=[x for x in prepared if x['cell']['key'][0]!=f and x['cell']['key'][6]!=k];assert train
  weights={side:collections.defaultdict(Q) for side in ['left','right']}
  for x in train:
   sign=-1 if x['cell']['key'][0] in flipped else 1
   for side in weights:
    for v,q in x['weights'][side].items():weights[side][v]+=sign*q/len(train)
  cellresults=[]
  for x in prepared:
   c=x['cell']
   if (c['key'][0],c['key'][6])!=(f,k):continue
   scores=[sum((weights[side].get(e[side],Q(0)) for side in ['left','right']),Q(0))/2 for e in c['events']];labels=[(e['label']=='OUTER')!=(f in flipped) for e in c['events']];outer=[q for q,l in zip(scores,labels) if l];inner=[q for q,l in zip(scores,labels) if not l];auc=sum((Q(1) if a>b else Q(1,2) if a==b else Q(0) for a in outer for b in inner),Q(0))/(len(outer)*len(inner));row=dict(key=c['key'],auc=number(auc))
   if detail:row['events']=[dict(id=e['id'],label='OUTER' if label else 'INNER',score=number(q),known={side:e[side] in weights[side] for side in ['left','right']}) for e,q,label in zip(c['events'],scores,labels)]
   cellresults.append(row)
  mean=sum((Q(r['auc']['exact']) for r in cellresults),Q(0))/len(cellresults);fold=dict(folio=f,kernel=k,auc=number(mean),cells=cellresults)
  if detail:fold['model']=dict(training_cells=len(train),training_folios=sorted({x['cell']['key'][0] for x in train}),weights={side:{v:str(q) for v,q in sorted(ww.items())} for side,ww in weights.items()})
  foldresults.append(fold)
 kernels={k:sum((Q(x['auc']['exact']) for x in foldresults if x['kernel']==k),Q(0))/sum(x['kernel']==k for x in foldresults) for k in ['cth','ckh']};overall=sum(kernels.values(),Q(0))/2
 return dict(overall=number(overall),kernels={k:number(q) for k,q in kernels.items()},folds=foldresults) if detail else overall
def null_run(prepared,s,observed):
 folios=sorted({x['cell']['key'][0] for x in prepared});free=folios[1:];exact=len(folios)<=s['exact_max_folios'];rng=random.Random(s['seed']);patterns=itertools.product([0,1],repeat=len(free)) if exact else ([rng.getrandbits(1) for _ in free] for n in range(s['permutations']));rows=[]
 for bits in patterns:
  flipped={f for f,b in zip(free,bits) if b};auc=evaluate(prepared,flipped);rows.append(dict(bits=list(bits),auc=number(auc),at_least_observed=auc>=observed))
 tail=sum(r['at_least_observed'] for r in rows);p=Q(tail,len(rows)) if exact else Q(1+tail,1+len(rows));return dict(unit='WHOLE_PHYSICAL_FOLIO_POLARITY',folios=folios,fixed_folio=folios[0],free_folios=free,exact_enumeration=exact,patterns=rows,tail=tail,p=number(p))
def fixture():
 cs=[]
 for f,k in [(1,'cth'),(2,'cth'),(3,'ckh'),(4,'ckh')]:
  ev=[dict(id=f'{f}o',label='OUTER',left='alpha',right='alpha'),dict(id=f'{f}i',label='INNER',left='beta',right='beta')];cs.append(dict(key=[f,'fixture','P','X','1','ch',k,'EARLY'],events=ev,mixed=True))
 pp=prepare(cs);assert evaluate(pp)==1 and evaluate(pp,{1,2,3,4})==1
 for c in cs:
  for e in c['events']:e['left']=e['right']='unknown'+str(c['key'][0])
 assert evaluate(prepare(cs))==Q(1,2)
 def synthetic(f,k,signal):
  ev=[dict(id=f'{f}{k}o',label='OUTER',left='alpha' if signal else 'flat',right='alpha' if signal else 'flat'),dict(id=f'{f}{k}i',label='INNER',left='beta' if signal else 'flat',right='beta' if signal else 'flat')]
  return dict(key=[f,'fixture','P','X','1','ch',k,'EARLY'],events=ev,mixed=True)
 leakage=[synthetic(1,'cth',True),synthetic(1,'ckh',True),synthetic(2,'cth',False),synthetic(2,'ckh',False),synthetic(3,'ckh',False)]
 detail=evaluate(prepare(leakage),detail=True);assert next(x['auc']['exact'] for x in detail['folds'] if (x['folio'],x['kernel'])==(1,'cth'))=='1/2'
 wrongkernel=[synthetic(1,'cth',True),synthetic(2,'cth',True),synthetic(3,'ckh',False),synthetic(4,'ckh',False)]
 detail=evaluate(prepare(wrongkernel),detail=True);assert all(x['auc']['exact']=='1/2' for x in detail['folds'] if x['kernel']=='cth')
 print('FIXTURE_DIRECTION_UNKNOWN_TIES_GLOBAL_FLIP_AND_TWO_LEAKAGE_TRAPS_PASS')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');ap.add_argument('--fixture',action='store_true');a=ap.parse_args()
 if a.fixture:fixture();return
 s=json.loads((E/'src/SPEC.json').read_text());raw=(ROOT/s['source']).read_bytes();assert hashlib.sha256(raw).hexdigest()==s['source_sha256'];events=extract(json.loads(raw),s);cells=cells_for(events);cap=capacity(cells,s)
 save('EVENTS.json',events,a.check);save('CELLS.json',cells,a.check);result=dict(status='CAPACITY_STOP_NO_MODEL_OR_NULL',events=len(events),capacity=cap)
 if cap['pass_all']:
  prepared=prepare(cells);observed=evaluate(prepared,detail=True);null=null_run(prepared,s,Q(observed['overall']['exact']));success=Q(observed['overall']['exact'])>=Q('0.65') and all(Q(q['exact'])>Q(1,2) for q in observed['kernels'].values()) and Q(null['p']['exact'])<=Q('0.01');save('OBSERVED.json',observed,a.check);save('NULL.json',null,a.check);result.update(status='NARROW_CROSS_KERNEL_TRANSFER_PASS' if success else 'FIXED_CROSS_KERNEL_COMPARATOR_FAIL',overall=observed['overall'],kernels=observed['kernels'],null_p=null['p'],exact_null=null['exact_enumeration'],null_patterns=len(null['patterns']))
 else:assert not (E/'artifacts/OBSERVED.json').exists() and not (E/'artifacts/NULL.json').exists()
 save('RESULT.json',result,a.check);print(enc(result))
if __name__=='__main__':main()
