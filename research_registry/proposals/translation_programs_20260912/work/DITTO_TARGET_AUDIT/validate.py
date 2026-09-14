"""Direct source extraction check; no independent semantic validation."""
import hashlib,json
from pathlib import Path
b=Path(__file__).resolve().parent;r=b.parents[4]
s=json.loads((b/'SOURCE.json').read_text())
for p,h in s['sources'].items(): assert hashlib.sha256((r/p).read_bytes()).hexdigest()==h
assert hashlib.sha256((b/'DECISION.md').read_bytes()).hexdigest()==s['decision_sha256']
a=json.loads((b/'AUDIT.json').read_text()); packets=json.loads((b/'PARAGRAPHS.json').read_text())
assert len(a)==5
for edition in ['ZL3b','IT2a']:
 count=0;mismatch=[]
 for case in a:
  hits=case['readings'][edition];assert len(hits)==1
  hit=hits[0];p=next(p for p in packets if p['edition']==edition and p['id']==hit['paragraph'])
  line=next(l for l in p['lines'] if l['locus']==hit['locus']);assert line['words']==hit['words']
  flat=[(l['locus'],w) for l in p['lines'] for w in l['words']]
  matching=[i for i,x in enumerate(flat) if x==(case['locus'],case['surface_display'])];assert len(matching)==1
  i=matching[0];obs=hit['occurrences'][0]
  assert list(flat[i+1])==obs['source_successor']
  if flat[i+1]!=(case['selected_next_locus'],case['selected_next_surface']):mismatch.append(case['event_id'])
  count+=int(obs['symmetric'])
 assert count==1 and mismatch==['E238']
p=next(p for p in packets if p['edition']=='ZL3b' and any(l['locus']=='f83r.3' for l in p['lines']))
assert sum(len(l['words']) for l in p['lines'] if l['locus'] in ['f83r.4','f83r.5'])==19
print('PASS: 5 cases in 2 alternate readings; direct neighbor check; 19 intervening ZL groups. No semantic validation.')
