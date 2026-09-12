#!/usr/bin/env python3
import csv,json,hashlib
from pathlib import Path
D=Path('research_registry/proposals/translation_programs_20260912/work/P25')
read=lambda n:list(csv.DictReader((D/n).open(),delimiter='\t'))
inp=json.loads((D/'INPUT.json').read_text())
for prefix in ['herb','label']:
 assert hashlib.sha256(Path(inp[prefix+'_source']).read_bytes()).hexdigest()==inp[prefix+'_sha256']
raw=[(f"{r['locus']}:{i}",w) for r in inp['lines'] for i,w in enumerate(r['groups'],1)]
look=dict(raw)
for model in ['D','L']:
 a=read('ALIGNMENT_'+model+'.tsv');assert [(x['locus'],x['word']) for x in a]==raw
 for x in a:
  if x['role']=='VALUE' and x['target']!='UNBOUND':
   locus,i=x['locus'].rsplit(':',1);assert x['target']==locus+':'+str(int(i)-1)
for c in read('CONTRADICTIONS.tsv'):
 assert look[c['earlier_locus']]==c['earlier_property'] and look[c['later_locus']]==c['later_property']
 a={x['locus']:x for x in read('ALIGNMENT_'+c['model']+'.tsv')}
 assert a[c['earlier_locus']]['target']==a[c['later_locus']]['target']==c['target']
lab=read('ALL_LABEL_GROUPS.tsv');assert [(x['locus'],x['word']) for x in lab]==[(r['locus']+':'+str(i),w) for r in inp['labels'] for i,w in enumerate(r['raw'].split(),1)]
assert len(lab)==16 and sum(int(x['exact_hypothesis_match']) for x in lab)==0
out={'status':'PASS','scope':'source hashes, 145 groups in both readings, every conflict endpoint and value adjacency, all 16 label groups; no semantic truth','confirmed_meanings':0}
(D/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
