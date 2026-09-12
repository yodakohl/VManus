import csv,json,hashlib
from pathlib import Path
D=Path('research_registry/proposals/translation_programs_20260912/work/P21')
def read(n):return list(csv.DictReader((D/n).open(),delimiter='\t'))
s=json.loads((D/'SOURCE.json').read_text());p=Path(s['source'])
assert hashlib.sha256(p.read_bytes()).hexdigest()==s['sha256']
assert hashlib.sha256((D/'DECISION.md').read_bytes()).hexdigest()==s['decision_sha256']
x=json.loads(p.read_text());seq=[(r['locus'].split('.')[0],r['locus']+':'+str(i),w) for r in x['lines'] for i,w in enumerate(r['groups'],1)]
assert len(seq)==145
for m in ['F','R','L']:assert [(r['record'],r['at'],r['word']) for r in read('ALIGNMENT_'+m+'.tsv')]==seq
model=json.loads((D/'MODEL.json').read_text());nouns=model['nouns'];verbs=model['verbs'];bs=read('ALL_BINDINGS.tsv');idx={a:i for i,(_,a,_) in enumerate(seq)}
assert [b['at'] for b in bs]==[a for _,a,w in seq if w in verbs]
for b in bs:
 i=idx[b['at']];direction=verbs[b['word']][1];candidate='';j=i+direction
 while 0<=j<len(seq):
  r,a,w=seq[j]
  if r!=b['record'] or w in verbs:break
  if w in nouns:candidate=a;break
  j+=direction
 assert b['target']==candidate
 for m in ['F','R']:
  expected='MISSING' if not candidate else 'MATCH' if nouns[seq[j][2]][m+'_case']=='OBJECT' else 'FORM_CONFLICT'
  assert b[m]==expected
occ=read('ALL_NOUN_OCCURRENCES.tsv');assert [(o['record'],o['at'],o['word']) for o in occ]==[t for t in seq if t[2] in nouns]
for o in occ:assert o['governors']==','.join(b['at'] for b in bs if b['target']==o['at'])
result=json.loads((D/'RESULT.json').read_text())
assert result['hypothesis_positions']==sum(w in nouns or w in verbs for _,_,w in seq)
for m,counts in result['summary'].items():
 for status,count in counts.items():assert count==sum(b[m]==status for b in bs)
(D/'VALIDATION.json').write_text(json.dumps(dict(status='PASS',checks=['source and decision hashes','all145groups in three alignments','all14verbs','independent bounded nearest-noun scan','case-direction comparison','all25noun occurrences and governors','summary counts'],limitation='No independent meaning or case identification'),indent=2)+'\n')
print('PASS')
