#!/usr/bin/env python3
"""Read-back audit of source conservation and every claimed temporal link."""
import csv,json,hashlib
from pathlib import Path
D=Path(__file__).parent
read=lambda p:list(csv.DictReader(p.open(),delimiter='\t'))
s=read(D.parent/'P12/PROSE.tsv')
raw={(r['record_id'],f"{r['locus']}:{i}"):w for r in s for i,w in enumerate(r['zl3b_line'].split(),1)}
receipt=json.loads((D/'SOURCE.json').read_text())
assert hashlib.sha256((D.parent/'P12/PROSE.tsv').read_bytes()).hexdigest()==receipt['sha256']
events=read(D/'EVENTS.tsv');links=0
for model in ['I','R']:
 a=read(D/('ALIGNMENT_'+model+'.tsv'))
 assert len(a)==341 and {(x['record'],x['locus']):x['word'] for x in a}==raw
 ev=[e for e in events if e['model']==model]; lookup={e['locus']:e for e in ev}
 assert len(ev)==42 and len(lookup)==42
 for e in ev:
  assert raw[e['record'],e['locus']]==e['word']
  for field in ['prior_completed_event','state_used_by_heat','cause_or_start']:
   if e[field]=='NA':continue
   for loc in e[field].split(';'):
    p=lookup[loc];assert p['record']==e['record'] and p['patient']==e['patient']
    assert int(p['narrative_position'])<=int(e['narrative_position'])
    if field=='state_used_by_heat':assert p['kind'] in ['DIRECT','STATE','COMPLETE'] and p['destination']!='MISSING';links+=1
    elif field=='prior_completed_event':assert p['kind'] in ['DIRECT','STATE','COMPLETE']
  if e['word']=='qoteedy':assert e['prior_completed_event']=='NA'
assert links==2
result={'status':'PASS','scope':'source conservation, all 84 event positions, every emitted temporal link; no semantic validation','state_input_links_checked':links,'confirmed_meanings':0}
(D/'READBACK_VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
