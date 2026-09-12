from pathlib import Path
import csv,json,hashlib,itertools
D=Path(__file__).resolve().parent;R=next(p for p in D.parents if (p/'vmanus-work').exists())
def rows(p):
 with p.open() as f:return list(csv.DictReader(f,delimiter='\t'))
for x in json.loads((D/'SOURCE.json').read_text())['files']:assert hashlib.sha256((R/x['path']).read_bytes()).hexdigest()==x['sha256']
s=rows(D.parent/'S05/INPUT.tsv');d=rows(D/'DECISIONS.tsv');assert len(s)==145 and len(d)==6
for m in ['FIRST','LAST']:
 a=rows(D/f'ALIGNMENT_{m}.tsv');assert [(x['at'],x['word']) for x in a]==[(x['at'],x['word']) for x in s]
 text=(D/f'READING_{m}.md').read_text()
 for locus in dict.fromkeys(x['locus'] for x in s):assert '`'+' '.join(x['word'] for x in s if x['locus']==locus)+'`' in text
for i in range(0,6,2):assert d[i]['expected']==d[i+1]['expected'] and d[i]['result']==d[i+1]['result']
assert {x['decision_at']:x['claim_at'] for x in d if x['mode']=='LAST'}=={'f17r.5:9':'f17r.5:4','f21r.9:4':'NONE','f21r.12:8':'f21r.12:5'}
sp=rows(D/'SPANS.tsv');assert len(sp)==5
assert [x['complete_text'] for x in sp]==['EMPTY','cphor cphaldy dair cthey','fcho kshy otor sheol ocphal opsheas cthodaiin oty okaiin sho tshaiin','sheey ysheol','chol daiin']
for x in rows(D/'ALL_COMPANION_OCCURRENCES.tsv'):
 loci=[z['at'] for z in s if z['word']==x['word']];assert len(loci)==int(x['count']) and ','.join(loci)==x['all_loci']
# Finite cross-check of the general equality/inequality proof; not a significance control.
cases=0
for n in range(1,7):
 for a in itertools.product('AB',repeat=n):
  for q in ['dry','wet','unknown']:
   reduced='REJECT' if len(set(a))>1 else ('ACCEPT' if n>1 and q=='dry' else 'UNKNOWN')
   for i in range(n):
    raw='REJECT' if any(v!=a[i] for j,v in enumerate(a) if j!=i) else ('ACCEPT' if n>1 and q=='dry' else 'UNKNOWN')
    assert raw==reduced;cases+=1
v={'status':'PASS','coverage':'sources,145groups,all6direction rows,all5complete spans,all companion occurrences,general reduction finite cross-check','algebra_crosschecks':cases,'semantic_validation':False,'search_null_control':False}
(D/'VALIDATION.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
