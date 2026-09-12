"""Independent segmentation reconstruction and NP interval grammar audit."""
import csv,json,hashlib
from pathlib import Path
from collections import Counter
D=Path('research_registry/proposals/translation_programs_20260912/work/P22')
def rr(n):return list(csv.DictReader((D/n).open(),delimiter='\t'))
src=json.loads((D/'SOURCE.json').read_text())
for p,h in src['inputs'].items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
orig=json.loads((D.parent/'P11/INPUT.json').read_text())['lines'];flat=[]
for line in orig:
 for i,w in enumerate(line['groups'],1):flat.append((line['locus'].split('.')[0],line['locus'],f'{line["locus"]}:{i}',w))
assert [(r['record'],r['line'],r['locus'],r['word']) for r in rr('INPUT.tsv')]==flat
heads={'ctho','cthy','chor','shor','chocthy','cthaiin','keol','chy','okaiin','otchol'};verbs={'sho','qotchy'}
npall=rr('NOUN_PHRASES.tsv');caseall=rr('CASE_MARKERS.tsv');opsall=rr('OPERATIONS.tsv')
for mode in ['W','M']:
 elements=rr(f'ELEMENTS_{mode}.tsv');expected=[]
 for rec,line,loc,w in flat:
  splits=[w]
  if mode=='M' and len(w)>5 and w[-5:]=='daiin':splits=[w[:-5],w[-5:]]
  es=[e for e in elements if e['locus']==loc];assert [e['piece'] for e in es]==splits
  assert ''.join(e['piece'] for e in es)==w
  cursor=0
  for e in es:
   assert int(e['start'])==cursor;cursor=int(e['end']);assert w[int(e['start']):cursor]==e['piece']
  assert cursor==len(w)
 # NP intervals are bounded directly by the next head, verb, or record boundary.
 boundaries=[i for i,e in enumerate(elements) if e['piece'] in heads|verbs or (e['bound']=='YES' and e['piece']!='daiin')]
 expected_nps=[]
 for idx in boundaries:
  e=elements[idx]
  if e['piece'] in verbs:continue
  end=next((k for k in range(idx+1,len(elements)) if k in boundaries or elements[k]['record']!=e['record']),len(elements))
  boundcases=[x for x in elements[idx+1:end] if x['piece']=='daiin']
  known=e['piece'] in heads
  expected_nps.append({'id':e['element_id'],'index':idx,'end':end,'head':e['piece'],'known':known,'case':'OBJECT' if known and boundcases else 'UNMARKED','case_sources':','.join(x['element_id'] for x in boundcases) or 'NONE'})
  n=next(n for n in npall if n['mode']==mode and n['np_id']==e['element_id'])
  assert n['head']==e['piece'] and n['case']==expected_nps[-1]['case'] and n['case_sources']==expected_nps[-1]['case_sources']
  expected_end=elements[end]['element_id'] if end<len(elements) and elements[end]['record']==e['record'] else 'RECORD_END'
  assert n['end_before']==expected_end
 assert len(expected_nps)==len([n for n in npall if n['mode']==mode])
 for idx,e in enumerate(elements):
  if e['piece']!='daiin':continue
  possible=[n for n in expected_nps if n['index']<idx<n['end']];n=possible[-1] if possible else None
  priorcase=any(x['piece']=='daiin' for x in elements[n['index']+1:idx]) if n else False
  status='MISSING_HEAD' if n is None else 'UNKNOWN_STEM' if not n['known'] else 'DUPLICATE_CASE' if priorcase else 'MARKED_OBJECT'
  c=next(c for c in caseall if c['mode']==mode and c['element_id']==e['element_id'])
  assert c['status']==status and c['head']==(n['head'] if n else 'NA')
 expectedops=[]
 for idx,e in enumerate(elements):
  if e['piece'] not in verbs:continue
  end=next((k for k in range(idx+1,len(elements)) if elements[k]['line']!=e['line'] or elements[k]['piece'] in verbs),len(elements))
  eligible=[n for n in expected_nps if idx<n['index']<end and n['known']];n=eligible[0] if eligible else None
  status='MISSING_ARGUMENT' if not n else 'MATCH_OBJECT' if n['case']=='OBJECT' else 'UNMARKED_ARGUMENT'
  actual=next(o for o in opsall if o['mode']==mode and o['locus']==e['locus'])
  assert (actual['status'],actual['head'],actual['np_id'])==(status,n['head'] if n else 'NA',n['id'] if n else 'NA');expectedops.append(status)
 alignment=rr(f'ALIGNMENT_{mode}.tsv');assert [(r['record'],r['line'],r['locus'],r['word']) for r in alignment]==flat
 for a in alignment:
  es=[e for e in elements if e['locus']==a['locus']];known=sum(e['piece'] in heads|verbs|{'chol','shol','daiin'} for e in es)
  assert a['coverage']==('FULL_HYPOTHESIS' if known==len(es) else 'PARTIAL_HYPOTHESIS' if known else 'OPEN')
 text=(D/f'READING_{mode}.md').read_text();assert all('`'+l['raw_line']+'`' in text for l in orig)
 result=json.loads((D/'RESULT.json').read_text())['models'][mode]
 assert result['elements']==len(elements) and result['operations']==dict(Counter(expectedops))
 assert result['raw_coverage']==dict(Counter(a['coverage'] for a in alignment))
 assert result['case_occurrences']==dict(Counter(c['status'] for c in caseall if c['mode']==mode))
# Compare consequences without ignoring NP identity or unparsed intervening pieces.
strip=lambda mode:[{k:v for k,v in o.items() if k!='mode'} for o in opsall if o['mode']==mode]
assert strip('W')==strip('M')
splits=rr('ALL_SPLITS.tsv');assert [(s['locus'],s['pieces']) for s in splits]==[('f21r.8:7','ctho+daiin'),('f29v.3:5','o+daiin')]
assert len(opsall)==12 and len(caseall)==18 and len(flat)==145
assert all(n['used_by']=='NONE' for n in npall if n['head']=='ctho')
receipt={'status':'PASS','source_hashes':len(src['inputs']),'source_groups':145,'losslessly_checked_elements':292,'independent_case_rows':18,'independent_verb_rows':12,'all_verb_consequences_equal':True,'checks':['complete suffix-rule census','exact character interval roundtrip','direct NP boundary reconstruction','case duplication and unknown bound stem','all verb valencies','full paragraph readings'],'limit':'Execution and grammar under assumptions, not original spacing, phonetic values or language identification.'}
(D/'VALIDATION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
