import argparse,collections,hashlib,itertools,json,math,re
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]
def enc(x):return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=True)+'\n'
def save(name,x,check=False):
 p=E/'artifacts'/name
 if check:assert p.read_text()==enc(x),name
 else:p.write_text(enc(x))
def extract(source,s):
 out=[]
 for line in source['lines']:
  m=line['metadata'];assert m['edition']=='ZL3b' and m['page'] in s['allowed_selectors'] and not m['page'].startswith('f84')
  gs=[dict(zip(source['group_columns'],g)) for g in line['groups']];folio=int(re.match(r'f(\d+)',m['page'])[1])
  for start in range(1,len(gs)-1):
   for n in [1,2]:
    span=gs[start-1:start+n+1]
    if len(span)!=n+2 or not all(re.fullmatch('[a-z]+',g['ivtff_group_raw']) for g in span):continue
    if not all(int(b['source_group_index'])==int(a['source_group_index'])+1 and a['right_separator']==b['left_separator']=='DEFINITE_SPACE' for a,b in zip(span,span[1:])):continue
    target=span[1:-1];w=''.join(g['ivtff_group_raw'] for g in target);idx=target[0]['source_group_index']
    out.append(dict(id=f"ZL3b|{m['locus']}|{idx}-{target[-1]['source_group_index']}",W=w,form='JOINED' if n==1 else 'SPLIT',folio=folio,selector=m['page'],locus=m['locus'],kind=m['kind'],section=m['section'],hand=m['hand'],start_index=idx,source_ids=[g['source_group_id'] for g in target],target=[g['ivtff_group_raw'] for g in target],left=span[0]['ivtff_group_raw'],right=span[-1]['ivtff_group_raw'],fold='DISCOVERY' if folio%2==0 else 'HELD'))
 return out
def select(occ,s):
 counts=collections.Counter((o['W'],o['form']) for o in occ if o['fold']=='DISCOVERY');folios=collections.defaultdict(set)
 for o in occ:
  if o['fold']=='DISCOVERY':folios[o['W'],o['form']].add(o['folio'])
 words=[];qualified=set()
 for w in sorted({o['W'] for o in occ}):
  valid=all(counts[w,c]>=2 and len(folios[w,c])>=2 for c in ['JOINED','SPLIT'])
  words.append([w,counts[w,'JOINED'],sorted(folios[w,'JOINED']),counts[w,'SPLIT'],sorted(folios[w,'SPLIT']),valid])
  if valid:qualified.add(w)
 retained=[o for o in occ if o['W'] in qualified];groups=collections.defaultdict(lambda:collections.defaultdict(list))
 for o in retained:
  if o['fold']=='HELD':groups[tuple(o[k] for k in ['W','folio','selector','kind','section','hand','start_index'])][o['form']].append(o)
 candidates=collections.defaultdict(list)
 for key,classes in groups.items():
  for j,t in itertools.product(classes['JOINED'],classes['SPLIT']):
   metadata=list(key)+[j['id'],t['id']];canonical=json.dumps(metadata,ensure_ascii=True,separators=(',',':'));rank=hashlib.sha256(('853|'+canonical).encode()).hexdigest();candidates[key[1]].append(dict(metadata=metadata,rank=rank,canonical=canonical,joined_id=j['id'],split_id=t['id'],W=key[0],folio=key[1]))
 pairs=[min(v,key=lambda x:(x['rank'],x['canonical'])) for f,v in sorted(candidates.items())];wc=collections.Counter(p['W'] for p in pairs);n=len(pairs)
 gates=dict(minimum_folios=n>=8,minimum_wholes=len(wc)>=3,maximum_whole_fraction=bool(n) and max(wc.values(),default=0)<=n/2)
 capacity=dict(pass_all=all(gates.values()),gates=gates,selected_folios=n,selected_wholes=len(wc),whole_pair_counts=dict(wc),qualified_wholes=len(qualified),candidate_pairs=sum(map(len,candidates.values())),candidate_pairs_per_folio={str(f):len(v) for f,v in sorted(candidates.items())})
 return retained,words,pairs,capacity
def score(occ,pairs):
 byid={o['id']:o for o in occ};models={};diagnostics={c:{side:dict(known=0,unknown=0) for side in ['left','right']} for c in ['JOINED','SPLIT']}
 for w in sorted({p['W'] for p in pairs}):
  disc=[o for o in occ if o['W']==w and o['fold']=='DISCOVERY'];models[w]={}
  for side in ['left','right']:
   cs={c:collections.Counter(o[side] for o in disc if o['form']==c) for c in ['JOINED','SPLIT']};vocab=set(cs['JOINED'])|set(cs['SPLIT']);models[w][side]=dict(counts={c:dict(v) for c,v in cs.items()},N={c:sum(v.values()) for c,v in cs.items()},V=len(vocab)+1)
 scored=[]
 for pair in pairs:
  values={};components={}
  for form,key in [('JOINED','joined_id'),('SPLIT','split_id')]:
   o=byid[pair[key]];components[form]={}
   for side in ['left','right']:
    model=models[o['W']][side];v=o[side];known=any(v in model['counts'][c] for c in ['JOINED','SPLIT']);diagnostics[form][side]['known' if known else 'unknown']+=1
    contribution=math.log((model['counts']['SPLIT'].get(v,0)+1)/(model['N']['SPLIT']+model['V']))-math.log((model['counts']['JOINED'].get(v,0)+1)/(model['N']['JOINED']+model['V'])) if known else 0.
    components[form][side]=dict(neighbor=v,known=known,contribution=contribution)
   values[form]=sum(x['contribution'] for x in components[form].values())/2
  scored.append(dict(pair=pair,scores=values,components=components,correct=values['SPLIT']>values['JOINED'],tie=values['SPLIT']==values['JOINED']))
 n=len(scored);correct=sum(x['correct'] for x in scored);nontied=sum(not x['tie'] for x in scored)
 result=dict(n=n,correct=correct,nontied=nontied,accuracy=correct/n,success=correct/n>=.875 and nontied>=8,known_unknown_by_class_side=diagnostics)
 return models,scored,result
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');a=ap.parse_args();s=json.loads((E/'src/SPEC.json').read_text());raw=(ROOT/s['source']).read_bytes();assert hashlib.sha256(raw).hexdigest()==s['source_sha256'];source=json.loads(raw)
 occ=extract(source,s);retained,words,pairs,capacity=select(occ,s)
 result=dict(status='CAPACITY_STOP_NO_PREDICTOR_SCORE',source_sha256=s['source_sha256'],eligible_occurrences=len(occ),eligible_by_fold_form=dict(collections.Counter(o['fold']+'_'+o['form'] for o in occ)),capacity=capacity)
 for name,obj in [('OCCURRENCES.json',retained),('WHOLE_CAPACITY.json',dict(columns=['W','discovery_joined_n','discovery_joined_folios','discovery_split_n','discovery_split_folios','qualifies'],rows=words)),('HELD_PAIRS.json',pairs)]:save(name,obj,a.check)
 if capacity['pass_all']:
  models,scored,scores=score(retained,pairs);save('PREDICTOR.json',models,a.check);save('SCORED_PAIRS.json',scored,a.check);result['scores']=scores;result['status']='DESCRIPTIVE_CONTEXT_TRANSFER_PASS' if scores['success'] else 'FIXED_CONTEXT_PREDICTOR_FAIL'
 else:assert not any((E/'artifacts'/n).exists() for n in ['PREDICTOR.json','SCORED_PAIRS.json'])
 save('RESULT.json',result,a.check);print(enc(result))
if __name__=='__main__':main()
