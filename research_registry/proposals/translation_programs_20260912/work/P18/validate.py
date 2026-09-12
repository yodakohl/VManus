#!/usr/bin/env python3
import csv,json,hashlib
from pathlib import Path
D=Path('research_registry/proposals/translation_programs_20260912/work/P18');read=lambda n:list(csv.DictReader((D/n).open(),delimiter='\t'))
s=json.loads((D/'SOURCE.json').read_text())
for key in ['input','fixed_model']:assert hashlib.sha256(Path(s[key]).read_bytes()).hexdigest()==s[key+'_sha256']
raw=[(r['locus']+':'+str(i),w) for r in json.loads(Path(s['input']).read_text())['lines'] for i,w in enumerate(r['groups'],1)]
m=json.loads(Path(s['fixed_model']).read_text());lookup=dict(raw);events=read('EVENTS.tsv')
assert len(events)==120
for rule in ['L','R','V']:
 for mode in ['LOCAL','CARRY']:
  a=read('ALIGNMENT_'+rule+'_'+mode+'.tsv');assert [(x['locus'],x['word']) for x in a]==raw
  byloc={x['locus']:x for x in a};pos={x['locus']:i for i,x in enumerate(a)}
  e=[x for x in events if x['rule']==rule and x['mode']==mode];assert len(e)==20
  for x in e:
   assert lookup[x['locus']]==x['word'] and x['word'] in m['predicates']
   if x['bearer']!='MISSING':
    p=byloc[x['bearer']];assert p['record']==x['record'] and pos[p['locus']]<pos[x['locus']] and p['word'] in m['materials'] and p['claimed_complement']=='0'
    if mode=='LOCAL':assert p['unit']==x['unit']
   if x['right_complement']!='NA':
    p=byloc[x['right_complement']];assert pos[p['locus']]==pos[x['locus']]+1 and p['unit']==x['unit'] and p['claimed_complement']=='1'
   if x['severed_candidate']!='NA':assert byloc[x['severed_candidate']]['unit']!=x['unit']
a=[(x['locus'],x['bearer'],x['right_complement']) for x in events if x['rule']=='L' and x['mode']=='CARRY']
b=[(x['locus'],x['bearer'],x['right_complement']) for x in events if x['rule']=='V' and x['mode']=='CARRY'];assert a==b
out={'status':'PASS','scope':'source/model hashes; every group, 120 predicate slots, every bound participant and right complement; L/CARRY and V/CARRY identical 20 bindings','meaning_or_boundaries_validated':False}
(D/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
