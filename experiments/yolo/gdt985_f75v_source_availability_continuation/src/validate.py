import hashlib,json,time
from pathlib import Path
from check_model import check,ground
E=Path(__file__).resolve().parents[1];R=E.parents[2];A=E/'artifacts'
t=time.monotonic()
for n,h in json.loads((E/'PREREG_LOCK.json').read_text())['files'].items():assert hashlib.sha256((R/n).read_bytes()).hexdigest()==h,n
packet=json.loads((A/'SOURCE_PACKET.json').read_text());original=json.loads((R/'experiments/yolo/gdt928_multi_anchor_complete_paragraphs/artifacts/PARAGRAPHS.json').read_text())
for ed,rows in packet['paragraphs'].items():assert rows==[p for p in original[ed] if p['id']=='f75v|f75v.38-f75v.42']
for ed,rows in packet['raw'].items():
 expected=[]
 for split in ['DISCOVERY','EVALUATION']:
  source=json.loads((R/f'experiments/yolo/gdt915_terminal_lr_phrase_transfer/artifacts/SOURCE_{split}_{ed}.json').read_text())
  for r in source['lines']:
   if r['metadata']['locus'] in {f'f75v.{i}' for i in range(38,43)}:expected.append({'metadata':r['metadata'],'groups':[dict(zip(source['group_columns'],g)) for g in r['groups']]})
 assert rows==sorted(expected,key=lambda r:int(r['metadata']['locus'].split('.')[1]))
queries=json.loads((A/'QUERIES.json').read_text());domains=json.loads((A/'WORD_DOMAINS.json').read_text());candidates=json.loads((A/'CANDIDATES.json').read_text());result=json.loads((A/'RESULT.json').read_text())
positive=0
for r in queries:
 lines=packet['paragraphs'][r['edition']][0]['lines'];selected=[l for l in lines if l['locus'] in ['f75v.40','f75v.41','f75v.42']]
 assert len(selected)==3 and all(l['anchor_eligible'] for l in selected)
 words=[w for l in selected for w in l['words']]
 independent=check(words,r['start'],r['query']);assert independent['status']==r['status'],(r['start'],r['query'],independent['status'],r['status'])
 if r['status']=='SAT':
  positive+=1;witness=r['witness'];ground(words,r['start'],witness['dictionary'],witness['states']);ground(words,r['start'],independent['dictionary'],independent['states'])
  q=r['query']
  if q['kind']=='word':assert witness['dictionary'][q['word']]==[q['code']//3,q['code']%3]
  if q['kind']=='final':assert witness['states'][-1]==q['state']
for d in domains:
 rel=[r for r in queries if r['edition']==d['edition'] and r['start']==d['start'] and r['query'].get('word')==d['word']]
 assert len(rel)==9 and {r['query']['code'] for r in rel}==set(range(9))
 for st,col in [('SAT','possible_codes'),('UNKNOWN','unknown_codes')]:assert d[col]==[r['query']['code'] for r in rel if r['status']==st]
 words=[w for l in packet['paragraphs'][d['edition']][0]['lines'] if l['locus'] in ['f75v.40','f75v.41','f75v.42'] for w in l['words']]
 assert d['positions']==[i for i,w in enumerate(words) if w==d['word']]
for ed in packet['raw']:
 pp=packet['paragraphs'].get(ed,[]);ls=[l for l in pp[0]['lines'] if l['locus'] in ['f75v.40','f75v.41','f75v.42']] if pp else []
 eligible=len(ls)==3 and all(l['anchor_eligible'] for l in ls)
 assert result['capacity'][ed]['eligible']==eligible
 if eligible:
  words=[w for l in ls for w in l['words']];unknown=set(words)-{'ol','or','qol','sheedy'}
  for start in [0,1]:
   qq=[r for r in queries if r['edition']==ed and r['start']==start]
   assert len(qq)==len(unknown)*9+3
   assert {d['word'] for d in domains if d['edition']==ed and d['start']==start}==unknown
 else:assert all(r['status']=='NO_CAPACITY' for r in candidates if r['edition']==ed)
assert len(candidates)==15
old={r['model']:r for r in json.loads((R/'experiments/yolo/gdt982_reciprocal_flow_clause_readings/artifacts/RESULT.json').read_text())['local_outcomes']}
for ed in packet['raw']:
 assert {r['candidate'] for r in candidates if r['edition']==ed}==set(old)
for r in candidates:
 assert r['inherited_status']==old[r['candidate']]['status']
 if result['capacity'][r['edition']]['eligible']:
  if r['candidate']=='DESCRIPTION':assert r['status']=='DESCRIPTION_UNSCORED'
  elif r['candidate']=='NOT_REPEAT':assert r['status']=='INHERITED_CONTRADICTION'
  else:
   base=next(q for q in queries if q['edition']==r['edition'] and q['start']==r['initial'] and q['query']['kind']=='base')
   assert r['status']=='CONTINUATION_'+base['status']
expected_tsv='edition\tstart\tword\tpositions_zero_based\tpossible_codes\tunknown_codes\n'
for d in domains:expected_tsv+='\t'.join(str(d[k]) if k in ['edition','start','word'] else ','.join(map(str,d[k])) for k in ['edition','start','word','positions','possible_codes','unknown_codes'])+'\n'
assert (A/'WORD_DOMAINS.tsv').read_text()==expected_tsv
for r in candidates:
 if r['status'].startswith('CONTINUATION_'):
  assert r['initial']==(0 if r['candidate']=='NOT_ONCE' else 1)
  dd=next(d for d in domains if d['edition']==r['edition'] and d['start']==r['initial'] and d['word']=='sheolo')
  assert r['sheolo_codes']==dd['possible_codes'] and r['sheolo_unknown']==dd['unknown_codes']
  assert r['forced_B_to_A']==(bool(dd['possible_codes']) and not dd['unknown_codes'] and all(c%3==0 for c in dd['possible_codes']))
  assert r['final_states']==[q['query']['state'] for q in queries if q['edition']==r['edition'] and q['start']==r['initial'] and q['query']['kind']=='final' and q['status']=='SAT']
for st,n in result['query_counts'].items():assert n==sum(r['status']==st for r in queries)
assert result['domain_rows']==len(domains) and result['candidate_rows']==len(candidates)
v={'status':'PASS','query_count':len(queries),'independently_grounded_positive_witnesses':positive,'domain_rows':len(domains),'candidate_rows':len(candidates),'complete_raw_lines':sum(map(len,packet['raw'].values())),'semantic_confirmation':False,'elapsed_seconds':time.monotonic()-t}
(A/'VALIDATION.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v,indent=2))
