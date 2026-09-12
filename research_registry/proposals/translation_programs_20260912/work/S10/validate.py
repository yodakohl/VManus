from pathlib import Path
import csv,json,hashlib
D=Path(__file__).resolve().parent;R=next(p for p in D.parents if (p/'vmanus-work').exists())
def rows(p):
 with p.open() as f:return list(csv.DictReader(f,delimiter='\t'))
for x in json.loads((D/'SOURCE.json').read_text())['files']:assert hashlib.sha256((R/x['path']).read_bytes()).hexdigest()==x['sha256']
s=rows(D.parent/'S05/INPUT.tsv');lex=json.loads((D/'MODEL.json').read_text())['lexicon']
assert len(s)==145
for m in ['T','L']:
 a=rows(D/f'ALIGNMENT_{m}.tsv');assert [(x['at'],x['word']) for x in a]==[(x['at'],x['word']) for x in s]
 assert sum(x['status']=='HYPOTHESIS' for x in a)==19
 text=(D/f'READING_{m}.md').read_text()
 for locus in dict.fromkeys(x['locus'] for x in s):assert '`'+' '.join(x['word'] for x in s if x['locus']==locus)+'`' in text
 for w in lex:assert len({x['gloss'] for x in a if x['word']==w})==1
out=rows(D/'ALL_DECISIONS.tsv');assert len(out)==3
expected={'f17r.5:9':('f17r.5:3','f17r.5:4','REJECT','MODEL_MATCH'),'f21r.9:4':('NONE','NONE','UNKNOWN','UNBOUND'),'f21r.12:8':('f21r.12:2','f21r.12:5','ACCEPT','MODEL_MATCH')}
assert {x['at']:(x['claim_at'],x['feature_loci'],x['expected'],x['result']) for x in out}==expected
for x in out:
 i=next(i for i,z in enumerate(s) if z['at']==x['at']);prefix=[z for z in s[:i] if z['record']==x['record']];heads=[z for z in prefix if z['word'] in {'chor','shor'}];q=[z for z in prefix if z['word'] in {'chol','shol'}]
 inferred='UNKNOWN'
 if heads:
  if any(z['word']!=heads[0]['word'] for z in heads[1:]):inferred='REJECT'
  elif len(heads)>1 and q and q[-1]['word']=='chol':inferred='ACCEPT'
 assert inferred==x['expected'];assert x['list_role_ablation']=='UNKNOWN_WITHOUT_CLAIM_ROLE'
assert sum(x['swapped_result']=='MODEL_CONTRADICTION' for x in out)==2
v={'status':'PASS','coverage':'immutable sources,145groups,both full readers,all6class mentions and3decisions,independent prefix reconstruction,global decision swap','semantic_validation':False,'search_significance_control':False}
(D/'VALIDATION.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
