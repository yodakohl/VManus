#!/usr/bin/env python3
import csv,json,hashlib
from pathlib import Path
D=Path('research_registry/proposals/translation_programs_20260912/work/P04');read=lambda n:list(csv.DictReader((D/n).open(),delimiter='\t'))
s=json.loads((D/'SOURCE.json').read_text())
for k in ['input','base_model']:assert hashlib.sha256(Path(s[k]).read_bytes()).hexdigest()==s[k+'_sha256']
source=json.loads(Path(s['input']).read_text())['lines'];raw=[(r['locus']+':'+str(i),w) for r in source for i,w in enumerate(r['groups'],1)]
ops=read('OPERATIONS.tsv');net=read('SUBSTITUTION_NETWORK.tsv');backs=[]
for scenario in ['S_A','S_B','L_AB']:
 a=read('ALIGNMENT_'+scenario+'.tsv');assert [(x['locus'],x['word']) for x in a]==raw
 lookup={x['locus']:x for x in a};idx={x['locus']:i for i,x in enumerate(a)}
 for r in source:
  text=' '.join(x['word'] for x in a if x['locus'].rsplit(':',1)[0]==r['locus']);assert text==r['raw_line'];backs.append({'scenario':scenario,'locus':r['locus'],'reconstructed_source':text,'status':'EXACT_FROM_ANNOTATED_POSITIONS_NOT_GERMAN_ALONE'})
 for e in [x for x in ops if x['scenario']==scenario]:
  if e['kind'] in ['ADD','PURPOSE']:
   assert idx[e['target']]==idx[e['locus']]+1 and lookup[e['target']]['claimed_by']==e['locus']
  if e['kind']=='ADD' and ':choice@' not in e['subject']:assert idx[e['subject']]<idx[e['locus']]
 choice=next(e for e in ops if e['scenario']==scenario and e['kind'] in ['CHOICE','JOINT_USE'])
 assert choice['target']=={'S_A':'chocthy','S_B':'cthaiin','L_AB':'chocthy+cthaiin'}[scenario]
 oil=next(e for e in ops if e['scenario']==scenario and e['locus']=='f32v.10:1');water=next(e for e in ops if e['scenario']==scenario and e['locus']=='f32v.11:2')
 assert oil['subject']==choice['subject'] and lookup[oil['target']]['word']=='keol'
 assert water['subject']=='f32v.10:8' and lookup[water['target']]['word']=='chy'
assert len(net)==1 and net[0]['original']=='chocthy' and net[0]['replacement']=='cthaiin'
assert not read('NETWORK_CHAINS.tsv')
with (D/'BACKTRANSLATION.tsv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(backs[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(backs)
out={'status':'PASS','scope':'source hashes; 3x145 groups; all 51 line backprojections; all additions/purposes, choices and shared oil versus separate water; no functional equivalence validation','confirmed_meanings':0}
(D/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
