"""Independent source enumeration, metadata selection and score reconstruction."""
import collections,hashlib,itertools,json,math,re
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]
def read(n):return json.loads((E/'artifacts'/n).read_text())
s=json.loads((E/'src/SPEC.json').read_text());raw=(ROOT/s['source']).read_bytes();assert hashlib.sha256(raw).hexdigest()==s['source_sha256'];source=json.loads(raw);allocc=[]
for line in source['lines']:
 m=line['metadata'];assert m['page'] in s['allowed_selectors'] and not m['page'].startswith('f84') and m['edition']=='ZL3b';gs=[dict(zip(source['group_columns'],x)) for x in line['groups']]
 for i,x in enumerate(gs):
  for n in (1,2):
   if i==0 or i+n>=len(gs):continue
   block=gs[i-1:i+n+1];okay=True
   for g in block:
    if not re.fullmatch(r'[a-z]+',g['ivtff_group_raw']):okay=False
   for j in range(len(block)-1):
    if int(block[j+1]['source_group_index'])-int(block[j]['source_group_index'])!=1 or block[j]['right_separator']!='DEFINITE_SPACE' or block[j+1]['left_separator']!='DEFINITE_SPACE':okay=False
   if not okay:continue
   target=gs[i:i+n];folio=int(re.match(r'f([0-9]+)',m['page']).group(1));start=x['source_group_index'];end=target[-1]['source_group_index']
   allocc.append(dict(id=f"ZL3b|{m['locus']}|{start}-{end}",W=''.join(g['ivtff_group_raw'] for g in target),form=('JOINED','SPLIT')[n-1],folio=folio,selector=m['page'],locus=m['locus'],kind=m['kind'],section=m['section'],hand=m['hand'],start_index=start,source_ids=[g['source_group_id'] for g in target],target=[g['ivtff_group_raw'] for g in target],left=gs[i-1]['ivtff_group_raw'],right=gs[i+n]['ivtff_group_raw'],fold='DISCOVERY' if folio%2==0 else 'HELD'))
assert len({x['id'] for x in allocc})==len(allocc)
disc=collections.defaultdict(lambda:collections.defaultdict(list))
for o in allocc:
 if o['fold']=='DISCOVERY':disc[o['W']][o['form']].append(o)
qualified=set();wordrows=[]
for w in sorted({o['W'] for o in allocc}):
 j=disc[w]['JOINED'];t=disc[w]['SPLIT'];jf=sorted({o['folio'] for o in j});tf=sorted({o['folio'] for o in t});good=len(j)>=2 and len(t)>=2 and len(jf)>=2 and len(tf)>=2
 wordrows.append([w,len(j),jf,len(t),tf,good])
 if good:qualified.add(w)
assert read('WHOLE_CAPACITY.json')['rows']==wordrows
retained=[o for o in allocc if o['W'] in qualified];assert retained==read('OCCURRENCES.json')
# Index joined and split independently; shared metadata keys supply candidates.
joined=collections.defaultdict(list);split=collections.defaultdict(list)
for o in retained:
 if o['fold']=='HELD':
  key=(o['W'],o['folio'],o['selector'],o['kind'],o['section'],o['hand'],o['start_index']);(joined if o['form']=='JOINED' else split)[key].append(o)
perfolio=collections.defaultdict(list)
for key in sorted(set(joined)&set(split)):
 for j in joined[key]:
  for t in split[key]:
   metadata=list(key)+[j['id'],t['id']];canonical=json.dumps(metadata,separators=(',',':'),ensure_ascii=True);rank=hashlib.sha256(('853|'+canonical).encode('utf-8')).hexdigest();perfolio[key[1]].append(dict(metadata=metadata,canonical=canonical,rank=rank,joined_id=j['id'],split_id=t['id'],W=key[0],folio=key[1]))
pairs=[sorted(v,key=lambda p:(p['rank'],p['canonical']))[0] for f,v in sorted(perfolio.items())];assert pairs==read('HELD_PAIRS.json');wc=collections.Counter(p['W'] for p in pairs);n=len(pairs);gates=dict(minimum_folios=n>=8,minimum_wholes=len(wc)>=3,maximum_whole_fraction=n>0 and max(wc.values(),default=0)<=n/2)
r=read('RESULT.json');cap=dict(pass_all=all(gates.values()),gates=gates,selected_folios=n,selected_wholes=len(wc),whole_pair_counts=dict(wc),qualified_wholes=len(qualified),candidate_pairs=sum(len(v) for v in perfolio.values()),candidate_pairs_per_folio={str(f):len(v) for f,v in sorted(perfolio.items())})
assert r['capacity']==cap and r['eligible_occurrences']==len(allocc);assert r['eligible_by_fold_form']==dict(collections.Counter(o['fold']+'_'+o['form'] for o in allocc))
if not cap['pass_all']:
 assert r['status']=='CAPACITY_STOP_NO_PREDICTOR_SCORE' and 'scores' not in r
 assert not (E/'artifacts/PREDICTOR.json').exists() and not (E/'artifacts/SCORED_PAIRS.json').exists()
else:
 models=read('PREDICTOR.json');scored=read('SCORED_PAIRS.json');lookup={o['id']:o for o in retained};known={c:{side:dict(known=0,unknown=0) for side in ['left','right']} for c in ['JOINED','SPLIT']};correct=0;nontied=0
 for w in {p['W'] for p in pairs}:
  for side in ['left','right']:
   counters={c:collections.Counter(o[side] for o in disc[w][c]) for c in ['JOINED','SPLIT']};expected=dict(counts={c:dict(v) for c,v in counters.items()},N={c:len(disc[w][c]) for c in counters},V=len(set(counters['JOINED'])|set(counters['SPLIT']))+1);assert models[w][side]==expected
 for p,observed in zip(pairs,scored):
  assert observed['pair']==p;values={}
  for c,key in [('JOINED','joined_id'),('SPLIT','split_id')]:
   o=lookup[p[key]];terms=[]
   for side in ['left','right']:
    model=models[o['W']][side];v=o[side];familiar=v in model['counts']['JOINED'] or v in model['counts']['SPLIT'];known[c][side]['known' if familiar else 'unknown']+=1
    term=math.log((model['counts']['SPLIT'].get(v,0)+1)/(model['N']['SPLIT']+model['V']))-math.log((model['counts']['JOINED'].get(v,0)+1)/(model['N']['JOINED']+model['V'])) if familiar else 0.;terms.append(term)
    assert observed['components'][c][side]==dict(neighbor=v,known=familiar,contribution=term)
   values[c]=sum(terms)/2
  assert observed['scores']==values and observed['correct']==(values['SPLIT']>values['JOINED']) and observed['tie']==(values['SPLIT']==values['JOINED']);correct+=observed['correct'];nontied+=not observed['tie']
 assert len(scored)==n;expected=dict(n=n,correct=correct,nontied=nontied,accuracy=correct/n,success=correct/n>=.875 and nontied>=8,known_unknown_by_class_side=known);assert r['scores']==expected;assert r['status']==('DESCRIPTIVE_CONTEXT_TRANSFER_PASS' if expected['success'] else 'FIXED_CONTEXT_PREDICTOR_FAIL')
(E/'artifacts/VALIDATION.json').write_text(json.dumps(dict(status='PASS_INDEPENDENT_SOURCE_ENUMERATION_METADATA_SELECTION_AND_CONDITIONAL_SCORE_CHECK',eligible_occurrences=len(allocc),selected_pairs=n,scoring_executed=cap['pass_all'],semantic_validation=False),indent=2)+'\n');print('PASS')
