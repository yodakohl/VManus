"""Independent prefix-history replay; does not import builder."""
import csv,json,hashlib
from pathlib import Path
from collections import Counter
D=Path('research_registry/proposals/translation_programs_20260912/work/P24')
def rows(p): return list(csv.DictReader(p.open(),delimiter='\t'))
src=json.loads((D/'SOURCE.json').read_text())
for p,h in src['inputs'].items(): assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
original=[]
for fn,page in [('P12','f83r'),('P28','f82r')]:
 for r in rows(D.parent/fn/'PROSE.tsv'):
  if r['page']==page: original.append(r)
projected=rows(D/'PROSE.tsv')
assert [{k:v for k,v in r.items() if k!='row_status'} for r in projected]==original
flat=[]
for r in original:
 for i,w in enumerate(r['zl3b_line'].split(),1):flat.append((r['page'],r['record_id'],f'{r["locus"]}:{i}',w))
assert len(flat)==619
pred=rows(D/'PREDICTIONS.tsv'); expected_predictions=[]
for mode in ['R','I','L']:
 aligned=rows(D/f'ALIGNMENT_{mode}.tsv'); assert len(aligned)==len(flat)
 completed=[]
 for j,(page,record,loc,word) in enumerate(flat):
  out=aligned[j]; assert (out['page'],out['record'],out['locus'],out['word'])==(page,record,loc,word)
  prefix=[t for t in flat[:j] if t[1]==record]
  noun_map={'shedy':'A','lchedy':'C','qokaiin':'B' if mode!='L' else 'Bq','okaiin':'B' if mode!='L' else 'B0'}
  ms=[t for t in prefix if t[3] in ('shedy','lchedy')]
  ds=[t for t in prefix if t[3] in ('okaiin','qokaiin')]
  identity=prior=state=prediction=verdict='NA'
  if word in noun_map:
   identity=noun_map[word]; prev=[t for t in prefix if noun_map.get(t[3])==identity]
   prior=prev[-1][2] if prev else 'NA'; state='KNOWN' if prev else 'NEW'
  elif word in ('okeedy','qokeedy'):
   if ms and ds:
    identity=noun_map[ms[-1][3]]+'>'+noun_map[ds[-1][3]]
    if mode=='L':identity=word+':'+identity
    prev=[e for e in completed if e[0]==record and e[1]==identity]
    prior=prev[-1][2] if prev else 'NA';state='KNOWN' if prev else 'NEW';completed.append((record,identity,loc))
   else:state='UNRESOLVED'
  if word in ('okaiin','qokaiin','okeedy','qokeedy') and mode!='L':
   if state=='UNRESOLVED':verdict='UNRESOLVED'
   else:
    base='okaiin' if word in ('okaiin','qokaiin') else 'okeedy'
    q=(state=='KNOWN') if mode=='R' else (state=='NEW')
    prediction=('q' if q else '')+base;verdict='MATCH' if prediction==word else 'CONTRADICTION'
   expected_predictions.append(out)
  assert [out[k] for k in ['identity','prior','state','prediction','verdict']]==[identity,prior,state,prediction,verdict],(mode,loc)
 assert all(r['rendering']==f'⟦{r["word"]}⟧' for r in aligned if r['kind']=='open')
 reading=(D/f'READING_{mode}.md').read_text()
 for r in original:assert f'`{r["zl3b_line"]}`' in reading
assert pred==expected_predictions
result=json.loads((D/'RESULT.json').read_text())
for mode in ['R','I']:
 for page in ['f83r','f82r']:
  assert result['form_predictions'][mode][page]==dict(Counter(r['verdict'] for r in pred if r['mode']==mode and r['page']==page))
assert len(pred)==76
assert sum(r['word']=='okeedy' for r in pred if r['mode']=='R')==2
assert all(r['verdict']=='UNRESOLVED' for r in pred if r['word']=='okeedy')
assert not any(r['word']=='okaiin' for r in pred)
assert result['independent_meaning_confirmations']==0
receipt={'status':'PASS','source_hashes':len(src['inputs']),'aligned_groups_per_mode':len(flat),'independently_replayed_form_rows':len(pred),'scope':['f83r','f82r'],'checks':['bounded source equality','prefix-only reference and event reconstruction','complete three-mode alignment','all target occurrences','both base forms unresolved','no okaiin capacity','aggregate counters'],'limit':'Validates execution, not meanings or assumed identity.'}
(D/'VALIDATION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
