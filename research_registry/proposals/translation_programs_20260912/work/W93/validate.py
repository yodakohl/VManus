import csv,json,hashlib
from collections import Counter
from pathlib import Path
D=Path(__file__).resolve().parent
j=lambda n:json.loads((D/n).read_text())
for p,h in j('FROZEN_INPUTS.json').items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
src=j('SOURCE.json');assert hashlib.sha256(Path(src['source']).read_bytes()).hexdigest()==src['source_sha256'];assert hashlib.sha256((D/'PROSE.tsv').read_bytes()).hexdigest()==src['projection_sha256']
rows=list(csv.DictReader((D/'PROSE.tsv').open(),delimiter='\t'));assert {r['page'] for r in rows}=={'f77r','f82r'}
lex={e['name']:e['body'] for e in json.loads((D.parent/'W92/DEFINITIONS.json').read_text())}
def resolve(words):
 pending=[(w,()) for w in words];out=[]
 while pending:
  w,seen=pending.pop(0)
  if w not in lex:out.append(w);continue
  assert w not in seen
  pending=[(a,seen+(w,)) for a in lex[w]]+pending
 return out
pred=j('PREDICTIONS.json');assert len(pred)==13
for p in pred:assert p['expected_expression']==resolve([p['name']])
units=j('UNITS.json');n=0;seq=[]
for r in rows:
 words=r['zl3b_line'].split();seq.extend((r['page'],r['record_id'],r['locus']+':'+str(i+1),w) for i,w in enumerate(words))
 markers=[i for i,w in enumerate(words) if w=='qokedy']
 for k,i in enumerate(markers):
  start=markers[k-1]+2 if k else 0;body=words[start:i];name=words[i+1] if i+1<len(words) else ''
  u=units[n];n+=1
  assert u['marker']==r['locus']+':'+str(i+1) and u['name']==name and u['literal_body']==body
  assert u['body_loci']==[r['locus']+':'+str(x+1) for x in range(start,i)]
  assert u['observed_expression']==resolve(body)
  assert name not in lex and body and name!='qokedy'
  assert u['status']=='OUTSIDE_FROZEN_NAMES' and u['expected_expression']==[]
  assert u['multiset_equal'] is None and u['first_difference_position'] is None
assert n==len(units)==8
align=list(csv.DictReader((D/'ALIGNMENT.tsv').open(),delimiter='\t'))
assert [(a['page'],a['record'],a['at'],a['word']) for a in align]==seq
counts=Counter(t[3] for t in seq)
candidates=list(csv.DictReader((D/'CANDIDATES.tsv').open(),delimiter='\t'))
assert {c['name'] for c in candidates}==set(lex)
for c in candidates:
 assert c['verdict']=='NO_CAPACITY'
 assert int(c['matched'])==int(c['contradicted'])==int(c['unbound'])==0
 assert int(c['all_source_occurrences'])==counts[c['name']]
 assert c['expected_expression'].split()==resolve([c['name']])
r=j('RESULT.json');assert r['status']=='NO_APPLICABLE_FIXED_NAME_STOP'
assert r['unit_outcomes']=={'OUTSIDE_FROZEN_NAMES':8} and r['candidate_outcomes']=={'NO_CAPACITY':13}
assert r['source_lines']==len(rows)==72 and r['source_groups']==len(seq)==599 and r['records']==len({x[1] for x in seq})==6
# Comparison fixtures verify ordered symbolic identity, not semantic equivalence.
a=['one','two'];b=['two','one'];assert a!=b and Counter(a)==Counter(b)
assert resolve(['qoky'])==['cheeety']
assert resolve(['qoky','qoky'])!=resolve(['qoky'])
out={'status':'PASS','scope':'frozen W92 bytes and 13 predictions; complete 72-line/599-position replay; all eight marker units; 13 no-capacity verdicts; 63 known-name appearances counted without promoting them','independent_semantic_confirmation':False,'validator_author':'root; separate reconstruction, not a second observer','actual_identity_comparisons':0,'known_name_occurrences':sum(counts[n] for n in lex)}
assert out['known_name_occurrences']==63
(D/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
